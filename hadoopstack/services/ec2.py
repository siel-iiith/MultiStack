from time import sleep

from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import EC2RegionInfo

def make_connection(credentials):
    """
    A general function to connect cloud provider endpoing using EC2 API

    @param credentials: A dictionary containing ec2 specific parameters for
    connecting to the endpoint.
    @type credentials: dictionary

    @return A boto ec2 connection object
    """

    url = credentials['ec2_url']
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

    hs_region = EC2RegionInfo(name = credentials['ec2_region'], endpoint = url_endpoint)
    
    conn = EC2Connection(
                    aws_access_key_id = credentials['ec2_access_key'],
                    aws_secret_access_key = credentials['ec2_secret_key'],
                    is_secure = secure,
                    path = url_path,
                    region = hs_region
                    )
    return conn

def ec2_entities(job_name):
    """
    Returns the name of basic ec2_entities.
    * Keypair name
    * Security group for slaves
    * Security group for master

    @param job_name: User given name of the Job.
    @type job_name: string
    """

    keypair_name = "hadoopstack-" + job_name
    sec_slave = "hadoopstack-" + job_name + "-slave"
    sec_master = "hadoopstack-" + job_name + "-master"
    return keypair_name, sec_master, sec_slave

def associate_public_ip(conn, instance_id):
    """Associates public_ip with the instance"""

    for addr in conn.get_all_addresses():
        if addr.instance_id is '':
            addr.associate(instance_id)
            return

    addr = conn.allocate_address()
    addr.associate(instance_id)
    print "IP Associated:", addr.public_ip

def release_public_ips(conn, public_ips_list):
    """
    Releases public_ips attached to the instances

    @param public_ips_list: list of public public_ips
    @type public_ips_list: list
    """

    for addr in conn.get_all_addresses(addresses = public_ips_list):
        if addr.instance_id == '':
            addr.release()

def boot_instances(conn, 
                    number, 
                    keypair,
                    security_groups,
                    flavor,
                    image_id
                    ):
    """
    Boot Instances

    @param conn: EC2 connection object
    @type conn: boto.ec2.connection.EC2Connection

    @param number: number of instances to boot
    @type number: int

    @param keypair: Keypair name
    @type keypair: string

    @param security_groups: name of the security security_groups
    @type security_groups: string

    @param flavor: instance type
    @type flavor: string

    @type image_id: image-id
    @type image_id: string
    """

    reservation = conn.run_instances(image_id, int(number), int(number), keypair, security_groups, instance_type=flavor)
    
    for instance in reservation.instances:
        while instance.state == 'pending':
            sleep(4)
            print "waiting for instance status to update"
            instance.update()

        associate_public_ip(conn, instance.id)

    return reservation

def create_keypair(conn, keypair_name, key_dir = '/tmp'):
    """
    Creates keypair and saves it in key_dir directory

    @param conn: EC2 connection object
    @type conn: boto.ec2.connection.EC2Connection

    @param keypair_name: Keypair name
    @type keypair_name: string

    @param key_dir: Destination folder of keypair
    @type key_dir: string
    """

    keypair = conn.create_key_pair(keypair_name)
    keypair.save(key_dir)

    # TODO - Save this keypair file in the mongodb

def create_security_groups(conn, sec_master_name, sec_slave_name):
    """
    Creates Security groups.

    @param conn: EC2 connection object
    @type conn: boto.ec2.connection.EC2Connection

    @param sec_master_name: Name of master's security group
    @type sec_master_name: string

    @param sec_slave_name: Name of slave's security group
    @type sec_slave_name: string
    """

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
