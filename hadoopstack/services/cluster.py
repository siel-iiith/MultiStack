from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import EC2RegionInfo

from hadoopstack import config

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

def spawn_instances(conn, 
                    number, 
                    keypair,
                    security_groups,
                    image_id = config.DEFAULT_IMAGE_ID, 
                    flavor = config.DEFAULT_FLAVOR):
    
    return conn.run_instances(image_id, int(number), int(number), keypair, security_groups, instance_type=flavor)

def create_keypair(conn, keypair_name):
    
    keypair = conn.create_key_pair(keypair_name)
    keypair.save("/tmp")
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

def setup(data):

    cluster_name = data['cluster']['name']
    keypair_name = "hadoopstack-" + cluster_name
    sec_tt_name = "hadoopstack-" + cluster_name + "-tasktracker"
    sec_jt_name = "hadoopstack-" + cluster_name + "-jobtracker"

    conn = make_connection()
    create_keypair(conn, keypair_name)
    create_security_groups(conn, cluster_name)
    res_tt = spawn_instances(
        conn, 
        data['cluster']['node-recipes']['tasktracker'], 
        keypair_name,
        [sec_tt_name]
        )

    res_jt = spawn_instances(
        conn, 
        data['cluster']['node-recipes']['jobtracker'], 
        keypair_name,
        [sec_jt_name]
        )

    # Assign Public IP to jobtracker. Rest of the communication is to be done
    # through Internal IPs
    return