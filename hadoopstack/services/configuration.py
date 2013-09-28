import paramiko
import socket
import subprocess
from time import sleep

from hadoopstack import config

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

def configure_master(private_ip_address, key_location, job_name):
    subprocess.call(("knife bootstrap {0} -x ubuntu -i {1} \
        -N {2}-master --sudo -r 'recipe[hadoopstack::master]' \
        --no-host-key-verify".format(private_ip_address,
         key_location, job_name)).split())

def configure_slave(private_ip_address, key_location, job_name, count):
    subprocess.call(("knife bootstrap {0} -x ubuntu -i {1} \
        -N {2}-slave-{3} --sudo -r 'recipe[hadoopstack::slave]' \
        --no-host-key-verify".format(private_ip_address,
         key_location, job_name, count)).split())

def configure_cluster(data):
    '''
    Configure Hadoop on the cluster using Chef

    '''

    job_name = data['job']['name']

    key_location = config.DEFAULT_KEY_LOCATION + "/hadoopstack-" + job_name + ".pem"
    slave_count = 1

    for node in data['job']['nodes']:
        if not ssh_check(node['private_ip_address'], key_location):
            if node['role'] == 'master':
                print "Unable to ssh into master. Aborting!!!"
                return
            print "Unable to ssh into node {0}. Skipping it".format(node['private_ip_address'])
            continue

        if node['role'] == 'master':
            configure_master(node['private_ip_address'], key_location, job_name)

        elif node['role'] == 'slave':
            configure_slave(node['private_ip_address'], key_location, job_name, slave_count)
            slave_count += 1