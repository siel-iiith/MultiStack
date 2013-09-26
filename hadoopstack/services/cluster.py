from hadoopstack import config

import hadoopstack
import simplejson
    
from hadoopstack.dbOperations.db import get_node_objects
from hadoopstack.dbOperations.db import flush_data_to_mongo
from hadoopstack.dbOperations.db import update_private_ip_address

from hadoopstack.services.configuration import configure_cluster
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

    return ('Terminated Job', 200)


def list_clusters():
    clusters_dict = {"clusters": []}
    for i in list(hadoopstack.main.mongo.db.job.find()):
        clusters_dict["clusters"].append(i['cluster'])
    return clusters_dict
