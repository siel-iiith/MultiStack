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

from hadoopstack.dbOperations.db import getVMid
from hadoopstack.dbOperations.makedict import fetchDict

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

    sec_tt_name = "hadoopstack-" + cluster_name + "-tasktracker"
    sec_jt_name = "hadoopstack-" + cluster_name + "-jobtracker"
    sec_tt = conn.create_security_group(sec_tt_name, "Security group for the TaskTrackers")
    sec_jt = conn.create_security_group(sec_jt_name, "Security group for the JobTracker")

    # For now we'll authorize all the connections. We can add
    # granular rules later
    sec_tt.authorize(
        ip_protocol = "tcp",
        from_port = 1,
        to_port = 65535,
        cidr_ip = "0.0.0.0/0")

    sec_tt.authorize(
        ip_protocol = "udp",
        from_port = 1,
        to_port = 65535,
        cidr_ip = "0.0.0.0/0")

    sec_tt.authorize(
        ip_protocol = "icmp",
        from_port = -1,
        to_port = -1,
        cidr_ip = "0.0.0.0/0")  

    sec_jt.authorize(
        ip_protocol = "tcp",
        from_port = 1,
        to_port = 65535,
        cidr_ip = "0.0.0.0/0")

    sec_jt.authorize(
        ip_protocol = "udp",
        from_port = 1,
        to_port = 65535,
        cidr_ip = "0.0.0.0/0")    

    sec_jt.authorize(
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

def configure_cluster(node_ips, num_jt, num_tt, cluster_name):
    '''
    Configure Hadoop on the cluster using Chef

    '''

    key_location = config.DEFAULT_KEY_LOCATION + "/hadoopstack-" + cluster_name + ".pem"

    ssh_check(node_ips[0], key_location)
    subprocess.Popen(("knife bootstrap {0} -x ubuntu -i {1} -N {2}-master --sudo -r 'recipe[hadoopstack::master]' --no-host-key-verify".format(node_ips[0], key_location, cluster_name)).split())
    
    for tt in xrange(0,num_tt):
        ssh_check(node_ips[tt+1], key_location)
        subprocess.Popen(("knife bootstrap {0} -x ubuntu -i {1} -N {2}-slave-{3} --sudo -r 'recipe[hadoopstack::slave]' --no-host-key-verify".format(node_ips[tt+1], key_location, cluster_name, str(tt+1))).split())

def spawn(data):

    cluster_name = data['cluster']['name']
    keypair_name = "hadoopstack-" + cluster_name
    sec_tt_name = "hadoopstack-" + cluster_name + "-tasktracker"
    sec_jt_name = "hadoopstack-" + cluster_name + "-jobtracker"

    conn = make_connection()
    create_keypair(conn, keypair_name)
    create_security_groups(conn, cluster_name)
    res_tt = boot_instances(
        conn, 
        data['cluster']['node-recipes']['tasktracker'], 
        keypair_name,
        [sec_tt_name]
        )

    res_jt = boot_instances(
        conn, 
        data['cluster']['node-recipes']['jobtracker'], 
        keypair_name,
        [sec_jt_name]
        )

    listToReturn = []
    listToReturn.append(res_jt)
    listToReturn.append(res_tt)

    associate_public_ip(conn, res_jt.instances[0].id)

    return conn,listToReturn,keypair_name

def _create_cluster(data, cluster_id):

    # ToDo: Keep updating the status after crucial steps
    conn,reservationId,keypair_name = spawn(data)
    
    reserveId = [ i.id for i in reservationId]
    allVMDetails = getVMid(conn,reserveId)
    
    num_tt = int(data['cluster']['node-recipes']['tasktracker'])
    num_jt = int(data['cluster']['node-recipes']['jobtracker'])

    recipeList = []
    [recipeList.append("jobtracker")    for i in xrange(0,num_jt)]
    [recipeList.append("tasktracker")   for i in xrange(0,num_tt)]
    
    cluster_details = fetchDict(conn, allVMDetails, recipeList, reserveId)
    cluster_details['_id'] = cluster_id
    cluster_details['name'] = data['cluster']['name']
    hadoopstack.main.mongo.db.cluster.save(cluster_details)

    nodes_ips = []
    for r in reservationId:
        for i in r.instances:
            nodes_ips.append(str(i.private_ip_address))

    configure_cluster(nodes_ips, num_jt, num_tt, data['cluster']['name'])

    return

def create(data):

    # TODO: We need to create an request-check/validation filter before inserting

    cluster_details = {}
    hadoopstack.main.mongo.db.cluster.insert(cluster_details)

    id_t = str(cluster_details['_id'])
    create_ret = {}
    create_ret['cid'] = id_t

    Process(target = _create_cluster, args = (data, cluster_details['_id'])).start()
    
    return create_ret

def delete(cid):
    cluster_info = hadoopstack.main.mongo.db.cluster.find({"_id": objectid.ObjectId(cid)})[0]
    cluster_name = cluster_info['name']
    conn = make_connection()

    keypair = 'hadoopstack-' + cluster_name
    security_groups = ['hadoopstack-' + cluster_name + '-jobtracker', 
                'hadoopstack-' + cluster_name + '-tasktracker']


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
        i["_id"] = str(i["_id"])
        clusters_dict["clusters"].append(i)
    return clusters_dict


