from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import EC2RegionInfo

from hadoopstack import config
from time import sleep
from tempfile import mkstemp
from multiprocessing import Process

import socket
import hadoopstack
import simplejson
import paramiko
import subprocess

from hadoopstack.dbOperations.db import get_node_objects
from hadoopstack.dbOperations.db import flush_data_to_mongo
from hadoopstack.dbOperations.db import update_private_ip_address

from bson import objectid

def make_connection():
    url = config.EC2_URL
    url_endpoint = url.split('/')[2]
    url_port = url.split(':')[2].split('/')[0]
    url_path = url.split(url_port)[1]    
    
    hs_region = EC2RegionInfo(name = "siel", endpoint = url_endpoint)

    conn=EC2Connection(
                    aws_access_key_id = config.EC2_ACCESS_KEY,
                    aws_secret_access_key = config.EC2_SECRET_KEY,
                    is_secure = False,
                    path = url_path,
                    region = hs_region)
    return conn

def associate_public_ip(conn, instance_id):
    for addr in conn.get_all_addresses():
        if addr.instance_id is '':
            addr.associate(instance_id)
            return

    addr = conn.allocate_address()
    addr.associate(instance_id)
    print "IP Associated:", addr.public_ip

def release_public_ips(conn, public_ips_list):
    for addr in conn.get_all_addresses():
        if (addr.public_ip in public_ips_list) and addr.instance_id is None:
            addr.release()

def boot_instances(conn, 
                    number, 
                    keypair,
                    security_groups,
                    image_id = config.DEFAULT_IMAGE_ID, 
                    flavor = config.DEFAULT_FLAVOR):
    
    connx = conn.run_instances(image_id, int(number), int(number), keypair, security_groups, instance_type=flavor)
    
    while connx.instances[0].state == "pending":
        for res in conn.get_all_instances():
            if res.id == connx.id:
                connx = res
        sleep(1)
    return connx

def create_keypair(conn, keypair_name):
    
    keypair = conn.create_key_pair(keypair_name)
    keypair.save(config.DEFAULT_KEY_LOCATION)
#   hadoopstack.main.mongo.db.keypair.insert(keypair.__dict__)
    # TODO - Save this keypair file in the mongodb

def create_security_groups(conn, cluster_name):

    sec_slave_name = "hadoopstack-" + cluster_name + "-slave"
    sec_master_name = "hadoopstack-" + cluster_name + "-master"
    sec_slave = conn.create_security_group(sec_slave_name, "Security group for the slaves")
    sec_master = conn.create_security_group(sec_master_name, "Security group for the master")

    # For now we'll authorize all the connections. We can add
    # granular rules later
    sec_slave.authorize(
        ip_protocol = "tcp",
        from_port = 1,
        to_port = 65535,
        cidr_ip = "0.0.0.0/0")

    sec_slave.authorize(
        ip_protocol = "udp",
        from_port = 1,
        to_port = 65535,
        cidr_ip = "0.0.0.0/0")

    sec_slave.authorize(
        ip_protocol = "icmp",
        from_port = -1,
        to_port = -1,
        cidr_ip = "0.0.0.0/0")  

    sec_master.authorize(
        ip_protocol = "tcp",
        from_port = 1,
        to_port = 65535,
        cidr_ip = "0.0.0.0/0")

    sec_master.authorize(
        ip_protocol = "udp",
        from_port = 1,
        to_port = 65535,
        cidr_ip = "0.0.0.0/0")    

    sec_master.authorize(
        ip_protocol = "icmp",
        from_port = -1,
        to_port = -1,
        cidr_ip = "0.0.0.0/0")

def ssh_check(instance_ip, key_location):
    '''
    Check if the ssh is up and running
    '''

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    while(True):
        try:
            ssh.connect(hostname=instance_ip,
                        username="ubuntu",
                        key_filename=key_location)
        
        except socket.error, (value, message):
            if value == 113 or 111:
                print "checking for ssh..."
                sleep(1)
                continue
            else:
                print "socket.error: [Errno", value, "]", message
        
        break

def configure_cluster(data):
    '''
    Configure Hadoop on the cluster using Chef

    '''

    cluster_name = data['cluster']['name']

    key_location = config.DEFAULT_KEY_LOCATION + "/hadoopstack-" + cluster_name + ".pem"
    slave_count = 1

    for node in data['cluster']['nodes']:
        ssh_check(node['private_ip_address'], key_location)
        if node['role'] == 'master':
            subprocess.Popen(("knife bootstrap {0} -x ubuntu -i {1} -N {2}-master --sudo -r 'recipe[hadoopstack::master]' --no-host-key-verify".format(node['private_ip_address'], key_location, cluster_name)).split())
        elif node['role'] == 'slave':
            subprocess.Popen(("knife bootstrap {0} -x ubuntu -i {1} -N {2}-slave-{3} --sudo -r 'recipe[hadoopstack::slave]' --no-host-key-verify".format(node['private_ip_address'], key_location, cluster_name, str(slave_count))).split())
            slave_count += 1

def spawn(data):

    data['cluster']['status'] = 'spawning'
    flush_data_to_mongo('cluster', data)

    cluster_name = data['cluster']['name']
    keypair_name = "hadoopstack-" + cluster_name
    sec_slave = "hadoopstack-" + cluster_name + "-slave"
    sec_master = "hadoopstack-" + cluster_name + "-master"

    conn = make_connection()
    create_keypair(conn, keypair_name)
    create_security_groups(conn, cluster_name)

    data['cluster']['nodes'] = []

    master = data['cluster']['master']

    res_master = boot_instances(
        conn,
        1,
        keypair_name,
        [sec_master],
        flavor = master['flavor']
        )
    data['cluster']['nodes'] += get_node_objects(conn, "master", res_master.id)
    flush_data_to_mongo('cluster', data)

    associate_public_ip(conn, res_master.instances[0].id)

    for slave in data['cluster']['slaves']:
        res_slave = boot_instances(
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
    print "done done done"

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
    cluster_info = hadoopstack.main.mongo.db.cluster.find({"_id": objectid.ObjectId(cid)})[0]
    cluster_name = cluster_info['name']
    conn = make_connection()

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
                for vm in cluster_info['VMids']:
                    if instance.id == str(vm['id']):
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

    release_public_ips(conn, public_ips)

    return ('Deleted Cluster', 200)


def list_clusters():
    clusters_dict = {"clusters": []}
    for i in list(hadoopstack.main.mongo.db.cluster.find()):
        clusters_dict["clusters"].append(i['cluster'])
    return clusters_dict


