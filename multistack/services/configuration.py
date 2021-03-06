import socket
import subprocess
import random
from time import sleep

import paramiko
from flask import current_app

from multistack.services import ec2
from multistack.services.remote import Remote

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
                current_app.logger.info("checking for ssh...")
                sleep(1)
                continue
            else:
                current_app.logger.error("socket.error: [Errno {0}] {1}".format(value, message))

        except paramiko.SSHException:
            print "paramiko.error: connection refused. Discarding instance"
            return False
        
        return True

def setup_chefserver_hostname(
        chef_server_hostname,
        chef_server_ip,
        remote
        ):
    """
    Setup a static host resolution entry of chefserver in /etc/hosts

    @param chef_server_hostname: Chef server hostname
    @type chef_server_hostname: string

    @param chef_server_ip: IP address of the chef server
    @type chef_server_ip: string

    @param remote: Instance of remote.Remote class
    @type remote: remote.Remote instance
    """

    remote.run("echo -e '{0}\t{1}' | sudo tee -a /etc/hosts".format(
                                    chef_server_ip, chef_server_hostname))

def configure_master(ip_address, key_location, job_name, user,
                    chef_server_hostname, chef_server_ip):

    if not ssh_check(ip_address, key_location):
        print "Unable to ssh into master{0}. Aborting!!!".format(ip_address)
        return False

    remote = Remote(ip_address, user, key_location)

    setup_chefserver_hostname(chef_server_hostname, chef_server_ip, remote)

    out = subprocess.Popen(("knife bootstrap {0} -x {1} -i {2} \
            -N {3}-master --sudo -r 'recipe[multistack-cdh4::master]' \
            --no-host-key-verify".format(ip_address, user,
            key_location, job_name)).split(),
            stdout = subprocess.PIPE
            )
    for line in out.communicate()[0].split('\n'):
        current_app.logger.info(line)

    return True

def configure_slave(ip_address, key_location, job_name, user,
                    chef_server_hostname, chef_server_ip):

    if not ssh_check(ip_address, key_location):
        print "Unable to ssh into node {0}. Skipping it".format(ip_address)
        return False

    remote = Remote(ip_address, user, key_location)

    setup_chefserver_hostname(chef_server_hostname, chef_server_ip, remote)

    out = subprocess.Popen((
        "knife bootstrap {0} -x {1} -i {2} \
        -N {3}-slave-{4} --sudo -r 'recipe[multistack-cdh4::slave]' \
        --no-host-key-verify".format(ip_address,
            user, key_location, job_name,
            str(random.random()).split('.')[1])
        ).split(),
        stdout = subprocess.PIPE
    )
    for line in out.communicate()[0].split('\n'):
        current_app.logger.info(line)

    return True

def configure_cluster(data, user, general_config):
    '''
    Configure Hadoop on the cluster using Chef

    '''

    job_name = data['job']['name']
    key_location = "/tmp/multistack-" + job_name + ".pem"
 
    for node in data['job']['nodes']:

        if node['role'] == 'master':
            if not configure_master(node['ip_address'], key_location, job_name,
                                user, general_config['chef_server_hostname'],
                                general_config['chef_server_ip']):
                return False

        elif node['role'] == 'slave':
            slave_public_ip = current_app.cloud.associate_public_ip(node['id'])
            configure_slave(slave_public_ip, key_location, job_name, user,
                                general_config['chef_server_hostname'],
                                general_config['chef_server_ip'])
            current_app.cloud.release_public_ip(slave_public_ip)

    return True
