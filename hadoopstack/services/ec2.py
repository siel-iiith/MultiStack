from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import EC2RegionInfo
from time import sleep

from hadoopstack import config
from hadoopstack.services.make_config_parser import configParserHelper

def make_connection(decider = "privateCloudConfig"):
    url = configParserHelper().get(decider,"EC2_URL")
    url_path = str()
    url_endpoint = url.split('/')[2]
    url_protocol = url.split('/')[0].split(':')[0]
    if url_protocol == "https":
        secure = True
    elif url_protocol == "http":
        secure = False

    if len(url.split(':')) > 2:
        url_port = url.split(':')[2].split('/')[0]
        url_path = url.split(url_port)[1]
    
    hs_region = EC2RegionInfo(name = configParserHelper().get(decider,"EC2_REGION"), endpoint = url_endpoint)
    
    conn=EC2Connection(
                    aws_access_key_id = configParserHelper().get(decider,"EC2_ACCESS_KEY"),
    
                    aws_secret_access_key = configParserHelper().get(decider,"EC2_SECRET_KEY"),
                    is_secure = secure,
                    path = url_path,
                    region = hs_region
                    )
    return conn

def ec2_entities(job_name):

    keypair_name = "hadoopstack-" + job_name
    sec_slave = "hadoopstack-" + job_name + "-slave"
    sec_master = "hadoopstack-" + job_name + "-master"
    return keypair_name, sec_master, sec_slave

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
                    flavor,
                    image_id ,
					decider = "privateCloudConfig"
                    ):
    
    connx = conn.run_instances(image_id, int(number), int(number), keypair, security_groups, instance_type=flavor)
    
    while connx.instances[0].state == "pending":
        for res in conn.get_all_instances():
            if res.id == connx.id:
                connx = res
        sleep(1)
    return connx

def create_keypair(conn, keypair_name):
    
    keypair = conn.create_key_pair(keypair_name)
    keypair.save(configParserHelper().get("commonConfig","DEFAULT_KEY_LOCATION"))
#  
#keypair.save(DEFAULT_KEY_LOCATION)
#   hadoopstack.main.mongo.db.keypair.insert(keypair.__dict__)
    # TODO - Save this keypair file in the mongodb

def create_security_groups(conn, sec_master_name, sec_slave_name):

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
