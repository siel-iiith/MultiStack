#!/usr/bin/python 

from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import EC2RegionInfo
from time import sleep
import paramiko

region_var = EC2RegionInfo(name="siel.openstack", endpoint="10.2.4.129:8773")
print region_var

# This a fixed image ID for our private cloud. Its ubuntu-12.04-amd64
default_image_id = "ami-00000010"
# The default minimum value of the no. of VMs to boot
default_min_vm = 1
default_key_location="/home/sahni/projects/HadoopStack/src/"

script_hadoop_install="https://raw.github.com/dharmeshkakadia/Hadoop-Scripts/master/hadoop_install.sh"

master_instance_flavor = "m1.tiny"
master_instance_number = 1
slaves_instance_flavor = "m1.tiny"
slaves_instance_number = 1


def cloud_provider(url):
    '''
    Function: cloud_provider()
    --------------------------
    Identify the cloud provider from the URL.

    @param url: endpoint url

    @return: a provider name(aws, hpcloud, openstack etc.)
    '''

    return "openstack"


def connect_cloud(access_key, secret_key, url):
    '''
    Function: connect_cloud(access_key, secret_key, url)
    ----------------------------------------------------
    This function uses ec2 API to connect to various cloud providers.
    Note that, it only connects to one cloud at a time.

    @param access_key: The EC2 access key.
    @param secret_key: The EC2 secret key.
    @param url: The EC2 API endpoint of the cloud.

    @return: NULL

    @todo: add support for other cloud providers

    '''
    global conn
    url_endpoint = url.split('/')[2]
    url_port = url.split(':')[2].split('/')[0]
    url_path = url.split(url_port)[1]
    url_protocol = url.split(":")[0]
    provider = cloud_provider(url)

    if provider == "openstack":
        if url_protocol == "http":
            conn = EC2Connection(access_key,
                    secret_key,
                    region=region_var,
                    is_secure=False,
                    path=url_path)
            return


def gen_save_keypair():
    '''
    Function: gen_save_keypair()
    -----------------------
    This function will generate a temporary keypair to be used by
    HadoopStack and save it in /tmp/HadoopStack directory.

    @return: bool: true or false, depicting success or failure respectively.

    @todo: Need to find a way to save this key securely. May be in per process
    tmp dir - /var/tmp/.

    '''

    list_key_pairs = conn.get_all_key_pairs("hadoopstack")
    if len(list_key_pairs) > 0:
        return

    key_pair = conn.create_key_pair("hadoopstack")
    key_pair.save(default_key_location)
    return


def spawn_instances(image_id, number, keypair, sec_group, flavor):
    '''
    Function: spawn_instances(number, flavor)
    -----------------------------------
    This function spawns virtual machines.

    @param number: The number of virtual machines to boot.
    @param flavor: The flavor of virtual machine, e.g. - m1.small etc.
    @param keypair: SSH keypair to be associated with each instance.
    @param image: Image to be booted.
    @param sec_group: list of security groups, the instances are going to be
    associated with.

    @return

    '''

    return conn.run_instances(default_image_id,
            int(default_min_vm),
            int(number),
            keypair,
            sec_group,
            flavor)


def create_sec_group():
    '''
    Function: create_sec_group()
    ---------------------------
    It creates a default "hadoopstack" security group for booting VMs.

    @return: security group.

    '''
    
    try:
        list_sec_groups = conn.get_all_security_groups(["hadoopstack"])
        print list_sec_groups
        if len(list_sec_groups) > 0:
            return list_sec_groups[0]

    except:
        sec_group = conn.create_security_group("hadoopstack",
                "Default security group for HadoopStack VMs")
        sec_group.authorize("icmp", "-1", "-1", "0.0.0.0/0")
        sec_group.authorize("tcp", "1", "65535", "0.0.0.0/0")
        sec_group.authorize("udp", "1", "65535", "0.0.0.0/0")

        return sec_group.id


def input_size_estimation(location_url):
    '''
    Function: input_size_estimation(location_url)
    ---------------------------------------------
    For the VM flavor and no. estimation we need the input size. This function
    uses basic logic to guess the approximate size of huge datasets.

    e.g - for one bucket(dir) and multiple files kind of data, this function
    calculates the avg. size of each object by using 5 random objects.

    avg_size_each_object = mean of n random objects(e.g. n=5)
    total_estimated_size = avg_size_each_object * no_of_objects

    @param location_url: location of input data(s3://, http://, hdfs:// etc.)

    @return: input_size in Bytes.

    '''


def refresh(resv_obj):
    '''
    Function: refresh(resv_obj)
    ---------------------------
    Most of the object values have to be updated to get the most recent values. This function takes care of it. As of now, only updated reservation objects are required.

    @param resv_obj: Its the reservation object
    
    @return resv_obj

    '''

    for res in conn.get_all_instances():
        if res.id == resv_obj.id:
            return res


def estimate_run_instances(input_size, deadline):
    '''
    Function: estimate_run_instances(conn_desc)
    -------------------------------------------
    This function estimates the number and flavor of instances based on the
    input size and deadline of the project.

    @return:

    '''

    master_resv_obj = spawn_instances(default_image_id,
            master_instance_number,
            "hadoopstack",
            ["hadoopstack"],
            master_instance_flavor)
   
    while True:
        if master_resv_obj.instances[0].state != "running":
            sleep(1)
            master_resv_obj = refresh(master_resv_obj)
            continue

        if master_resv_obj.instances[0].ip_address == \
                master_resv_obj.instances[0].private_ip_address:
            master_elastic_address = conn.allocate_address()
            master_elastic_address.associate(master_resv_obj.instances[0])
            print "Address", master_elastic_address.public_ip, "associated"
            break

    slaves_resv_obj = spawn_instances(default_image_id,
            slaves_instance_number,
            "hadoopstack",
            ["hadoopstack"],
            slaves_instance_flavor)

    return


def configure_instances(master_resv_obj, slave_resv_obj, script_location):
    '''
    Function: configure_system(master_resv_obj, slave_resv_obj)
    --------------------------------------------
    This function accesses and executes the script, specified by script_location
    , on master.

    @param master_resv_obj: Master node reservation object
    @param slave_resv_obj: Slave nodes reservation object
    @param script_location: Location of the script to be executed on the master.

    '''
