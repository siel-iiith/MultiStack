import boto
from boto.ec2.regioninfo import EC2RegionInfo
from boto.ec2.connection import EC2Connection
from fabric.api import *
import fabric
from time import sleep
import socket

siel_cloud_region = EC2RegionInfo(name="siel", endpoint="10.2.4.129:8773")
print siel_cloud_region

conn = EC2Connection("trial123", "trial123", region=siel_cloud_region, is_secure=False, path='services/Cloud')

res_id = conn.run_instances('ami-00000024',
                1,
                1,
                'demo',
                ['default'],
                instance_type='m1.tiny')

instance = res_id.instances[0]
print "Instance booted", instance.id

while res_id.instances[0].state == "pending":
    for res in conn.get_all_instances():
        if res.id == res_id.id:
            res_id = res
    sleep(1)

print res_id.instances[0].state

eip = conn.allocate_address()
print eip
conn.associate_address(instance.id, public_ip=eip.public_ip)

env.reject_unknown_hosts=False
env.disable_known_hosts=True
env.host_string = str(eip.public_ip)
env.key_filename = "/home/sahni/demo.pem"
env.user = "ubuntu"

while(True):
    try:
        run("hostname")
        break

    except fabric.exceptions.NetworkError:
        sleep(1)
        continue
