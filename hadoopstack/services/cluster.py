from hadoopstack import config
from multiprocessing import Process

import hadoopstack
import simplejson
import subprocess

from hadoopstack.dbOperations.db import get_node_objects
from hadoopstack.dbOperations.db import flush_data_to_mongo
from hadoopstack.dbOperations.db import update_private_ip_address

from hadoopstack.services.configuration import configure_cluster
from hadoopstack.services import ec2

from bson import objectid

def spawn(data):

    data['cluster']['nodes'] = []
    data['cluster']['status'] = 'spawning'
    flush_data_to_mongo('cluster', data)

    cluster_name = data['cluster']['name']
    keypair_name, sec_master, sec_slave = ec2.ec2_entities(cluster_name)

    conn = ec2.make_connection()
    ec2.create_keypair(conn, keypair_name)
    ec2.create_security_groups(conn, sec_master, sec_slave)

    master = data['cluster']['master']

    res_master = ec2.boot_instances(
        conn,
        1,
        keypair_name,
        [sec_master],
        flavor = master['flavor']
        )
    data['cluster']['nodes'] += get_node_objects(conn, "master", res_master.id)
    flush_data_to_mongo('cluster', data)

    ec2.associate_public_ip(conn, res_master.instances[0].id)

    for slave in data['cluster']['slaves']:
        res_slave = ec2.boot_instances(
            conn,
            slave['instances'],
            keypair_name,
            [sec_slave],
            flavor = slave['flavor']
            )
        data['cluster']['nodes'] += get_node_objects(conn, "slave", res_slave.id)
        flush_data_to_mongo('cluster', data)

    update_private_ip_address(conn, data)

    return

def _create_cluster(data, cluster_id):

    # ToDo: Keep updating the status after crucial steps
    spawn(data)

    configure_cluster(data)

    return

def create(data):

    # TODO: We need to create an request-check/validation filter before inserting

    cluster_details = data
    hadoopstack.main.mongo.db.cluster.insert(cluster_details)

    id_t = str(cluster_details['_id'])
    data['cluster']['id'] = id_t
    flush_data_to_mongo('cluster', data)

    create_ret = {}
    create_ret['cid'] = id_t

    Process(target = _create_cluster, args = (data, cluster_details['_id'])).start()
    
    return create_ret

def delete(cid):
    cluster_info = hadoopstack.main.mongo.db.cluster.find({"_id": objectid.ObjectId(cid)})[0]['cluster']
    cluster_name = cluster_info['name']
    conn = ec2.make_connection()

    keypair = 'hadoopstack-' + cluster_name
    security_groups = ['hadoopstack-' + cluster_name + '-master', 
        'hadoopstack-' + cluster_name + '-slave']

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
                for node in cluster_info['nodes']:
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

    return ('Deleted Cluster', 200)


def list_clusters():
    clusters_dict = {"clusters": []}
    for i in list(hadoopstack.main.mongo.db.cluster.find()):
        clusters_dict["clusters"].append(i['cluster'])
    return clusters_dict
