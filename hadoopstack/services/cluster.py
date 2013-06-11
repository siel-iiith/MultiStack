from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import EC2RegionInfo

# import hadoopstack.services.config wont work here as this would require all
#variables to be addressed as hadoopstack.services.config.ec2_url for example
from hadoopstack.services import config
#from hadoopstack.services.config import *
#import config
import os
from time import sleep

def make_connection():
    #proxy=os.environ.get('http_proxy')
    foo = open("foo.txt", "a+")
    #foo.write("env variable should be here "+proxy)
    foo.flush()
    #del os.environ['http_proxy']
    url = config.ec2_url
    url_endpoint = url.split('/')[2]
    url_port = url.split(':')[2].split('/')[0]
    url_path = url.split(url_port)[1]
    print url, "  + ", url_endpoint, "+", url_port, "+", url_path
    print config.access_key
    print config.secret_key
    hs_region = EC2RegionInfo(name="siel", endpoint=url_endpoint)
    conn = EC2Connection(aws_access_key_id=config.access_key,
                         aws_secret_access_key=config.secret_key,
                         is_secure=False, path=url_path, region=hs_region)
    #os.environ['http_proxy']=proxy
    #foo.write("\nvariable set is in make connection"+proxy+"\n")
    foo.flush()
    return conn


#http://10.2.4.129:8773/services/cloud   +  10.2.4.129:8773 + 
#8773 + /services/cloud

def spawn_instances(conn, number, 
                    image_id = config.default_image_id, 
                    flavor = config.master_instance_flavor):
    #proxy=os.environ['http_proxy']
    foo = open("foo.txt","a+")

    #del os.environ['http_proxy']
    connx = conn.run_instances(image_id, int(number), int(number),config.keyName, None, flavor)
    #instance=connx.instances[0]
    while connx.instances[0].state == "pending":
        for res in conn.get_all_instances():
            if res.id == connx.id:
                connx = res
        sleep(1)
    #os.environ['http_proxy']=proxy
    #foo.write("\nvariable set is in make connection"+proxy+"\n")
    foo.flush()
    return connx

