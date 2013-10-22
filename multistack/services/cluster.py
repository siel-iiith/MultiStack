import simplejson
import sys
from bson import objectid
from time import sleep

from flask import current_app
    
import multistack
from multistack.dbOperations.db import get_node_objects
from multistack.dbOperations.db import flush_data_to_mongo
from multistack.providers import initiate_cloud
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

    cloud = current_app.cloud

    cloud.create_keypair(cloud.keypair)
    cloud.create_security_groups(cloud.master_security_group,
                            cloud.slave_security_group)

    master = data['job']['master']

    res_master = cloud.boot_instances(
        cloud.master_name,
        1,
        cloud.keypair,
        [cloud.master_security_group],
        flavor = master['flavor'],
		image_id = image_id
        )

    current_app.cloud.associate_public_ip(res_master.instances[0].id)

    data['job']['nodes'] += get_node_objects("master", res_master.id)
    flush_data_to_mongo('job', data)

    for slave in data['job']['slaves']:
        res_slave = cloud.boot_instances(
            cloud.slave_name,
            slave['instances'],
            cloud.keypair,
            [cloud.slave_security_group],
            flavor = slave['flavor'],
			image_id = image_id
            )
        data['job']['nodes'] += get_node_objects("slave", res_slave.id)
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
    initiate_cloud(cloud['provider'], data['job']['name'], cloud['auth'])
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

    initiate_cloud(job_info['cloud'], job_name, cloud['auth'])
    cloud = current_app.cloud
    conn = cloud.conn

    security_groups = [
                    cloud.master_security_group,
                    cloud.slave_security_group
                    ]

    instance_ids = list()

    for node in job_info['nodes']:
        instance_ids.append(node['id'])

    for addr in cloud.conn.get_all_addresses():
        for node in job_info['nodes']:
            if addr.instance_id == node['id']:
                cloud.release_public_ip(addr.public_ip)

    current_app.logger.info("Released Addresses")

    cloud.terminate_instances(instance_ids)

    current_app.logger.info("Terminated Instances")

    cloud.delete_keypair()

    current_app.logger.info("Deleted Keypairs")

    cloud.delete_security_groups(security_groups)

    current_app.logger.info("Deleted Security Groups")

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

    job_db_item = multistack.main.mongo.db.job.find_one({"_id": objectid.ObjectId(job_id)})
    job_obj = job_db_item['job']
    job_name = job_obj['name']
    new_node_obj_list = list()

    initiate_cloud(cloud['provider'], job_name, cloud['auth'])

    key_location = '/tmp/'  + current_app.cloud.keypair + '.pem'

    for slave in data['slaves']:
        res_slave = current_app.cloud.boot_instances(
                slave['instances'],
                current_app.cloud.keypair,
                [current_app.cloud.slave_security_group],
                slave['flavor'],
                cloud['default_image_id']
                )

        # Incrementing the number of slaves in job object
        for count in range (0, len(job_obj['slaves'])):
            if slave['flavor'] == job_obj['slaves'][count]['flavor']:
                job_obj['slaves'][count]['instances'] += 1

        node_obj = get_node_objects("slave", res_slave.id)
        job_obj['nodes'] += node_obj
        new_node_obj_list += node_obj
        job_db_item['job'] = job_obj
        flush_data_to_mongo('job', job_db_item)

    for new_node_obj in new_node_obj_list:
        slave_public_ip = current_app.cloud.associate_public_ip(new_node_obj['id'])
        configure_slave(slave_public_ip,
                        key_location, job_name, cloud['user'],
                        general_config['chef_server_hostname'],
                        general_config['chef_server_ip'])
        current_app.cloud.release_public_ip(slave_public_ip)

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

    job_db_item = multistack.main.mongo.db.job.find_one({"_id": objectid.ObjectId(job_id)})
    job_obj = job_db_item['job']
    job_name = job_obj['name']

    initiate_cloud(job_obj['cloud'], job_name, cloud['auth'])

    for slave in data['slaves']:
        for node in job_obj['nodes']:
            if slave['flavor'] == node['flavor'] and node['role'] != 'master':
                current_app.cloud.terminate_instances(node['id'].split())
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
