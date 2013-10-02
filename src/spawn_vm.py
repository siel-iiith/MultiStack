#!/usr/bin/python 

from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import EC2RegionInfo
from time import sleep
import os
import sys
import paramiko
import socket
import argparse


# This a fixed image ID for our private cloud. Its ubuntu-12.04-amd64
default_image_id = "ami-0000001a"
# The default minimum value of the no. of VMs to boot
default_min_vm = 1
default_key_location = os.path.expanduser("~/.hadoopstack")
default_properties_location = "/tmp/properties"

script_hadoop_install = "https://github.com/shredder12/Hadoop-Scripts/raw/master/main.sh"

master_instance_flavor = "m1.medium"
master_instance_number = 1
slaves_instance_flavor = "m1.medium"
slaves_instance_number = 1

# The global dictionary where all the argument keywords will be stored.
args_dict = dict()
cred_dict = dict()

def get_cli_arguments():
    '''
    Parse the command line arguments.
    '''
    
    parse = argparse.ArgumentParser(description="Run Hadoop on cloud")
    parse.add_argument('-i', '--input', required=True, help="S3 URL of the input data")
    parse.add_argument('-o', '--output', required=True, help="S3 URL of the output data")
    parse.add_argument('-j', '--jar', required=True, help="location of the jar file")
    parse.add_argument('-c', '--classpath', required=True, help="classpath")
    args = parse.parse_args()
    
    args_dict['input'] = args.input
    args_dict['output'] = args.output
    args_dict['jar'] = args.jar
    args_dict['classpath'] = args.classpath
    

def get_credentials_config_file():
    '''
    It fetches the EC2 credentials from hadoopstack's configuration file.
    default - ~/.hadoopstack/config
    
    @type cred_dict: dictionary
    @param cred_dict: A dictionary of credentials fetched from environment
    variables.
    
    @rtype: Dictionary
    @return: Updated dictionary
    '''
    
    if not os.path.exists(os.path.expanduser('~/.hadoopstack/config')):
        return cred_dict
    
    conf_fd = open(os.path.expanduser('~/.hadoopstack/config'), 'r')
    conf_content = conf_fd.readlines()
    for parameter in conf_content:
        option = parameter.split('=')[0]
        value = parameter.split('=')[1]
        if option == "EC2_ACCESS_KEY" or option == "ec2_access_key":
            cred_dict['ec2_access_key'] = value.split('\n')[0]
        elif option == "EC2_SECRET_KEY" or option == "ec2_secret_key":
            cred_dict['ec2_secret_key'] = value.split('\n')[0]
        elif option == "EC2_URL" or option == "ec2_url":
            cred_dict['ec2_url'] = value.split('\n')[0]
            
    return cred_dict


def get_credentials_env():
    '''
    Fetches the EC2 credentials from the environment.
    
    @rtype: Dictionary
    @return: A dictionary of the fetched credentials.
    '''
    
    if os.environ.has_key("EC2_ACCESS_KEY"):
        cred_dict['ec2_access_key'] = os.environ["EC2_ACCESS_KEY"]
    
    if os.environ.has_key("EC2_SECRET_KEY"):
        cred_dict['ec2_secret_key'] = os.environ["EC2_SECRET_KEY"]
        
    if os.environ.has_key("EC2_URL"):
        cred_dict['ec2_url'] = os.environ["EC2_URL"]
        
    return cred_dict
   

def cloud_provider(url):
    '''
    Identify the cloud provider from the URL.

    @param url: endpoint url

    @return: a provider name(aws, hpcloud, openstack etc.)
    '''

    return "openstack"


def connect_cloud():
    '''
    This function uses ec2 API to connect to various cloud providers.
    Note that, it only connects to one cloud at a time.

    @type cred_dict: dictionary
    @param cred_dict: A dictionary containing access, secret and 
    connection urls.

    @return: NULL

    @todo: add support for other cloud providers

    '''
    
    global conn
    url = cred_dict['ec2_url']
    url_endpoint = url.split('/')[2]
    url_port = url.split(':')[2].split('/')[0]
    url_path = url.split(url_port)[1]
    url_protocol = url.split(":")[0]
    provider = cloud_provider(url)
    
    # A default region is required by boto for initiating connection.
    region_var = EC2RegionInfo(name="tmp.hadoopstack", endpoint=url_endpoint)

    if provider == "openstack":
        if url_protocol == "http":
            conn = EC2Connection(cred_dict['ec2_access_key'],
                    cred_dict['ec2_secret_key'],
                    region=region_var,
                    is_secure=False,
                    path=url_path)
            print conn
    return


def gen_save_keypair():
    '''
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
    if not os.path.exists(default_key_location):
        os.mkdir(os.path.expanduser("~/.hadoopstack"))
    key_pair.save(default_key_location)
    return


def spawn_instances(image_id, number, keypair, sec_group, flavor):
    '''
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
    Most of the object values have to be updated to get the most recent values.
    This function takes care of it. As of now, only updated reservation objects
    are required.

    @param resv_obj: Its the reservation object
    
    @return resv_obj

    '''

    for res in conn.get_all_instances():
        if res.id == resv_obj.id:
            return res
        

def create_properties(master_resv_obj, slaves_resv_obj, master_public_ip, namenode=True):
    '''
    Create properties file to be fed to the hadoop_install script
    
    @type master_resv_obj: boto.ec2.instance.Reservation object
    @param master_resv_obj: Master node reservation object
    
    @type slaves_resv_obj: boto.ec2.instance.Reservation object 
    @param slaves_resv_obj: Slave nodes reservation object
    
    @type master_public_ip: string
    @param master_public_ip: Public IP of master node
    
    '''
    
    properties_fd = open(default_properties_location, 'w+')
    properties_fd.write("jobtracker\t" + 
                        master_resv_obj.instances[0].ip_address + 
                        ":54311" + 
                         '\n')
    if namenode:
        properties_fd.write("namenode\t" + 
                            master_resv_obj.instances[0].ip_address + 
                            ":54310" + 
                            '\n')
    
    while slaves_resv_obj.instances[-1].state != "running":
        slaves_resv_obj = refresh(slaves_resv_obj)
        sleep(1)
    
    for slave in slaves_resv_obj.instances:
        properties_fd.write("slave\t" + slave.ip_address + '\n')
        
    properties_fd.close()
    
    return


def estimate_run_instances():
    '''
    This function estimates the number and flavour of instances based on the
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
    
    create_properties(master_resv_obj, slaves_resv_obj,
                       master_elastic_address.public_ip.encode('ascii',
                                                               'ignore'),
                      True)
    
    configure_instances(master_resv_obj, slaves_resv_obj,
                        master_elastic_address.public_ip.encode('ascii',
                                                                'ignore'),
                        script_hadoop_install)
    
    return


def configure_instances(master_resv_obj, slaves_resv_obj, master_public_ip, script_location):
    '''
    This function accesses and executes the script, specified by 
    script_location, on master.
    
    @type master_resv_obj: boto.ec2.instance.Reservation object
    @param master_resv_obj: Master node reservation object
    
    @type slaves_resv_obj: boto.ec2.instance.Reservation object 
    @param slaves_resv_obj: Slave nodes reservation object
    
    @type master_public_ip: string
    @param master_public_ip: Public IP of master node
    
    @type script_location: string
    @param script_location: Location of the script to be executed on the master

    '''
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_location = default_key_location + "/hadoopstack.pem"
    script_name = script_location.split('/')[-1]
    
    while(True):
        try:
            ssh.connect(hostname=master_public_ip,
                        username="root",
                        key_filename=key_location)
        
        except socket.error, (value, message):
            if value == 113:
                sleep(1)
                continue
            else:
                print "socket.error: [Errno", value, "]", message 
        
        break

    sftp = ssh.open_sftp()
    sftp.put(key_location, "/root/hadoopstack.pem")
    sftp.put(default_properties_location, "/root/properties")
    sftp.close()

    stdin, stdout, stderr = ssh.exec_command("wget " + script_location)
    for line in stderr:
        print line
                                              
    ssh.exec_command("chmod a+x " + script_name)
    
    stdin, stdout, stderr = ssh.exec_command('./' + script_name + 
                                             ' /root/hadoopstack.pem' + 
                                             ' /root/properties')
    for line in stdout:
        print line
    ssh.close()
    
    
if __name__ == "__main__":
    get_credentials_env()
    get_credentials_config_file()
    connect_cloud()
    gen_save_keypair()
    create_sec_group()
    estimate_run_instances()
    
