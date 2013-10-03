import socket
import subprocess
import random
from time import sleep

import paramiko
from fabric.api import run
from fabric.api import env

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

        except paramiko.SSHException:
            print "paramiko.error: connection refused. Discarding instance"
            return False
        
        return True

def setup_chefserver_hostname(
        chef_server_hostname,
        chef_server_ip,
        remote_host_addr,
        remote_user,
        key_location
        ):
    """
    Setup a static host resolution entry of chefserver in /etc/hosts

    @param chef_server_hostname: Chef server hostname
    @type chef_server_hostname: string

    @param chef_server_ip: IP address of the chef server
    @type chef_server_ip: string

    @param remote_host_addr: IP address of the remote host on which
    host resolution is to be configured.
    @type remote_host_addr: string

    @param remote_user: user of the remote machine
    @type remote_user: string

    @param key_location: Location of the private key_location
    @type key_location: string

    """

    env.host_string = remote_host_addr
    env.key_filename = key_location
    env.user = remote_user
    env.disable_known_hosts=True

    run("echo -e '{0}\t{1}' | sudo tee -a /etc/hosts".format(chef_server_ip,
                                                        chef_server_hostname))

def configure_master(private_ip_address, key_location, job_name, user,
                    chef_server_hostname, chef_server_ip):

    if not ssh_check(private_ip_address, key_location):
        print "Unable to ssh into master{0}. Aborting!!!".format(private_ip_address)
        return False

    setup_chefserver_hostname(chef_server_hostname, chef_server_ip,
                            private_ip_address, user, key_location)

    subprocess.call(("knife bootstrap {0} -x {1} -i {2} \
        -N {3}-master --sudo -r 'recipe[hadoopstack::master]' \
        --no-host-key-verify".format(private_ip_address, user,
         key_location, job_name)).split())

    return True

def configure_slave(private_ip_address, key_location, job_name, user,
                    chef_server_hostname, chef_server_ip):

    if not ssh_check(private_ip_address, key_location):
        print "Unable to ssh into node {0}. Skipping it".format(private_ip_address)
        return False

    setup_chefserver_hostname(chef_server_hostname, chef_server_ip,
                            private_ip_address, user, key_location)

    subprocess.call((
        "knife bootstrap {0} -x {1} -i {2} \
        -N {3}-slave-{4} --sudo -r 'recipe[hadoopstack::slave]' \
        --no-host-key-verify".format(private_ip_address,
            user, key_location, job_name,
            str(random.random()).split('.')[1])
        ).split()
    )

    return True

def configure_cluster(data, user, general_config):
    '''
    Configure Hadoop on the cluster using Chef

    '''

    job_name = data['job']['name']
    key_location = "/tmp/hadoopstack-" + job_name + ".pem"
 
    for node in data['job']['nodes']:

        if node['role'] == 'master':
            if not configure_master(node['private_ip_address'], key_location, job_name, user,
                                general_config['chef_server_hostname'],
                                general_config['chef_server_ip']):
                return False

        elif node['role'] == 'slave':
            setup_chefserver_hostname(general_config['chef_server_hostname'], general_config['chef_server_ip'],
                                    node['private_ip_address'], user, key_location)
            configure_slave(node['private_ip_address'], key_location, job_name, user,
                                general_config['chef_server_hostname'],
                                general_config['chef_server_ip'])

    return True
