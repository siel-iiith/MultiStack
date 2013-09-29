from hadoopstack import config

import hadoopstack
import simplejson
    
from hadoopstack.dbOperations.db import get_node_objects
from hadoopstack.dbOperations.db import flush_data_to_mongo
from hadoopstack.dbOperations.db import update_private_ip_address

from hadoopstack.services.configuration import configure_cluster
from hadoopstack.services.configuration import configure_slave
from hadoopstack.services import ec2

from bson import objectid

def spawn(data):

    data['job']['nodes'] = []
    data['job']['status'] = 'spawning'
    flush_data_to_mongo('job', data)

    job_name = data['job']['name']
    keypair_name, sec_master, sec_slave = ec2.ec2_entities(job_name)

    conn = ec2.make_connection()
    ec2.create_keypair(conn, keypair_name)
    ec2.create_security_groups(conn, sec_master, sec_slave)

    master = data['job']['master']

    res_master = ec2.boot_instances(
        conn,
        1,
        keypair_name,
        [sec_master],
        flavor = master['flavor']
        )
    data['job']['nodes'] += get_node_objects(conn, "master", res_master.id)
    flush_data_to_mongo('job', data)

    ec2.associate_public_ip(conn, res_master.instances[0].id)

    for slave in data['job']['slaves']:
        res_slave = ec2.boot_instances(
            conn,
            slave['instances'],
            keypair_name,
            [sec_slave],
            flavor = slave['flavor']
            )
        data['job']['nodes'] += get_node_objects(conn, "slave", res_slave.id)
        flush_data_to_mongo('job', data)

    update_private_ip_address(conn, data)

    return

def create(data):

    # TODO: We need to create an request-check/validation filter before inserting

    spawn(data)
    configure_cluster(data)
    
    return

def delete(cid):
    job_info = hadoopstack.main.mongo.db.job.find({"_id": objectid.ObjectId(cid)})[0]['job']
    job_name = job_info['name']
    conn = ec2.make_connection()

    keypair = 'hadoopstack-' + job_name
    security_groups = ['hadoopstack-' + job_name + '-master', 
        'hadoopstack-' + job_name + '-slave']

    '''
    
    Instances take a while to terminate, till then their status is
    'shutting-down'. Complete termination is required for deletion  of
    Security Groups. Hence, we use a loop to verify complete termination.

    '''
    
    flag = True
    public_ips = []

    while flag:
        flag = False
        for res in conn.get_all_instances():
            for instance in res.instances:
                for node in job_info['nodes']:
                    if instance.id == str(node['id']):
                        try:
                            if instance.ip_address != instance.private_ip_address:
                                if instance.ip_address not in public_ips:
                                    public_ips.append(str(instance.ip_address))
                            instance.terminate()
                        except:
                            pass
                        flag = True
                        continue

    print "Terminated Instances"

    try:
        for kp in conn.get_all_key_pairs(keynames = [keypair]):
            kp.delete()

        print "Terminated keypairs"

    except:
        print "Error while deleting Keypair"

    try:
        for sg in conn.get_all_security_groups(groupnames = security_groups):
            print sg.delete() 
        
        print "Terminated Security Groups"

    except:
        print "Error while deleting Security Groups"

    ec2.release_public_ips(conn, public_ips)

    return True


def list_clusters():
    clusters_dict = {"clusters": []}
    for i in list(hadoopstack.main.mongo.db.job.find()):
        clusters_dict["clusters"].append(i['cluster'])
    return clusters_dict

def add_nodes(data, job_id):

    conn = ec2.make_connection()

    job_db_item = hadoopstack.main.mongo.db.job.find_one({"_id": objectid.ObjectId(job_id)})
    job_obj = job_db_item['job']
    job_name = job_obj['name']

    keypair_name, sec_master, sec_slave = ec2.ec2_entities(job_name)
    key_location = config.DEFAULT_KEY_LOCATION + '/'  + keypair_name + '.pem'

    for slave in data['slaves']:
        res_slave = ec2.boot_instances(
                conn,
                slave['instances'],
                keypair_name,
                [sec_master],
                flavor = slave['flavor']
                )

        # Incrementing the number of slaves in job object
        for count in range (0, len(job_obj['slaves'])):
            if slave['flavor'] == job_obj['slaves'][count]['flavor']:
                job_obj['slaves'][count]['instances'] += 1

        node_obj = get_node_objects(conn, "slave", res_slave.id)
        job_obj['nodes'] += node_obj
        job_db_item['job'] = job_obj
        flush_data_to_mongo('job', job_db_item)

        for node in node_obj:
            configure_slave(node['private_ip_address'], key_location, job_name)