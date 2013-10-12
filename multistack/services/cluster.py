import simplejson
import sys
from bson import objectid
from time import sleep

from flask import current_app
    
import multistack
from multistack.dbOperations.db import get_node_objects
from multistack.dbOperations.db import flush_data_to_mongo
from multistack.services.configuration import configure_cluster
from multistack.services.configuration import configure_slave
from multistack.services import ec2
from multistack.services.run import submit_job

def spawn(data, cloud):
    """
    Generates the keypair and creates security groups specific to the
    cluster and boots the instances.

    @param data: The job document stored in mongo database.
    @type data: dict

    @param cloud: Cloud object containing information of a specific
    cloud provider.
    @type cloud: dict
    """

    image_id = cloud['default_image_id']

    data['job']['nodes'] = []
    data['job']['status'] = 'spawning'
    flush_data_to_mongo('job', data)

    job_name = data['job']['name']
    keypair_name, sec_master, sec_slave = ec2.ec2_entities(job_name)

    conn = ec2.make_connection(cloud['auth'])
    ec2.create_keypair(conn, keypair_name)
    ec2.create_security_groups(conn, sec_master, sec_slave)

    master = data['job']['master']

    res_master = ec2.boot_instances(
        conn,
        1,
        keypair_name,
        [sec_master],
        flavor = master['flavor'],
		image_id = image_id
        )

    data['job']['nodes'] += get_node_objects(conn, "master", res_master.id)
    flush_data_to_mongo('job', data)

    for slave in data['job']['slaves']:
        res_slave = ec2.boot_instances(
            conn,
            slave['instances'],
            keypair_name,
            [sec_slave],
            flavor = slave['flavor'],
			image_id = image_id
            )
        data['job']['nodes'] += get_node_objects(conn, "slave", res_slave.id)
        flush_data_to_mongo('job', data)

    return

def create(data, cloud, general_config):
    """
    Creates the cluster - provisioning and configuration

    @param data: The job document stored in mongo database.
    @type data: dict

    @param cloud: Cloud object containing information of a specific
    cloud provider.
    @type cloud: dict

    @param general_config: General configuration parameters from multistack.configure_slave
    @type general_config: dict
    """

    # TODO: We need to create an request-check/validation filter before inserting

    current_app.logger.info('creating')
    spawn(data, cloud)
    configure_cluster(data, cloud['user'], general_config)
    submit_job(data, cloud['user'], cloud['auth'])
    
    return

def delete(cid, cloud):
    """
    Deletes the cluster

    @param cid: Cluster ID
    @type data: string

    @param cloud: Cloud object containing information of a specific
    cloud provider.
    @type cloud: dict
    """

    current_app.logger.info('deleting')

    job_info = multistack.main.mongo.db.job.find({"_id": objectid.ObjectId(cid)})[0]['job']
    job_name = job_info['name']

    conn = ec2.make_connection(cloud['auth'])

    keypair, sec_grp_master, sec_grp_slave = ec2.ec2_entities(job_name)
    security_groups = [sec_grp_master, sec_grp_slave]
    public_ips = list()

    for res in conn.get_all_instances():
        for instance in res.instances:
            for node in job_info['nodes']:
                if instance.id == str(node['id']):
                    instance.terminate()
    current_app.logger.info("Terminated Instances")

    for kp in conn.get_all_key_pairs():
        if kp.name == keypair:
            kp.delete()
    current_app.logger.info("Deleted Keypairs")

    while True:
        try:
            for sg in conn.get_all_security_groups(
                                                groupnames = security_groups):
                if len(sg.instances()) == 0:
                    sg.delete()
                    security_groups.remove(sg.name)
                else:
                    all_dead = True
                    for instance in sg.instances():
                        if instance.state != 'terminated':
                            # To stop code from requesting blindly
                            sleep(2)
                            all_dead = False

                    if all_dead:
                        sg.delete()
                        security_groups.remove(sg.name)
            if len(security_groups) == 0:
                current_app.logger.info("Deleted Security Groups")
                break;
        except:
            current_app.logger.error("Error:".format(sys.exc_info()[0]))
            break

    for node in job_info['nodes']:
        public_ips.append(node['ip_address'])

    if len(public_ips) > 0:
        ec2.release_public_ips(conn, public_ips)

    current_app.logger.info("Released Elastic IPs")

    return True

def list_clusters():
    clusters_dict = {"clusters": []}
    for i in list(multistack.main.mongo.db.job.find()):
        clusters_dict["clusters"].append(i['cluster'])
    return clusters_dict

def add_nodes(data, cloud, job_id, general_config):
    """
    Add nodes to a cluster and updates the job object

    @param data: The job document stored in mongo database.
    @type data: dict

    @param cloud: Cloud object containing information of a specific
    cloud provider.
    @type cloud: dict

    @param job_id: Job ID
    @type job_id: string

    @param general_config: General config parameters of multistack
    @type general_config: dict
    """

    conn = ec2.make_connection(cloud['auth'])

    job_db_item = multistack.main.mongo.db.job.find_one({"_id": objectid.ObjectId(job_id)})
    job_obj = job_db_item['job']
    job_name = job_obj['name']
    new_node_obj_list = list()

    keypair_name, sec_master, sec_slave = ec2.ec2_entities(job_name)
    key_location = '/tmp/'  + keypair_name + '.pem'

    for slave in data['slaves']:
        res_slave = ec2.boot_instances(
                conn,
                slave['instances'],
                keypair_name,
                [sec_master],
                slave['flavor'],
                cloud['default_image_id']
                )

        # Incrementing the number of slaves in job object
        for count in range (0, len(job_obj['slaves'])):
            if slave['flavor'] == job_obj['slaves'][count]['flavor']:
                job_obj['slaves'][count]['instances'] += 1

        node_obj = get_node_objects(conn, "slave", res_slave.id)
        job_obj['nodes'] += node_obj
        new_node_obj_list += node_obj
        job_db_item['job'] = job_obj
        flush_data_to_mongo('job', job_db_item)

    for new_node_obj in new_node_obj_list:
        configure_slave(new_node_obj['ip_address'],
                        key_location, job_name, cloud['user'],
                        general_config['chef_server_hostname'],
                        general_config['chef_server_ip'])

def remove_nodes(data, cloud, job_id):
    """
    Removes Nodes from a running cluster and updates the Job object.

    @param data: The job document stored in mongo database.
    @type data: dict

    @param cloud: Cloud object containing information of a specific
    cloud provider.
    @type cloud: dict

    @param job_id: Job ID
    @type job_id: string
    """

    conn = ec2.make_connection(cloud['auth'])

    job_db_item = multistack.main.mongo.db.job.find_one({"_id": objectid.ObjectId(job_id)})
    job_obj = job_db_item['job']

    for slave in data['slaves']:
        for node in job_obj['nodes']:
            if slave['flavor'] == node['flavor'] and node['role'] != 'master':
                conn.terminate_instances(node['id'].split())
                slave['instances'] -=1
                job_obj['nodes'].remove(node)
            if slave['instances'] == 0:
                break

    # Decrementing the number of slaves in job object
    for count in range (0, len(job_obj['slaves'])):
        if slave['flavor'] == job_obj['slaves'][count]['flavor']:
            job_obj['slaves'][count]['instances'] -= 1

    job_db_item['job'] = job_obj
    flush_data_to_mongo('job', job_db_item)
