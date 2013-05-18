from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import EC2RegionInfo

# import hadoopstack.services.config wont work here as this would require all variables to be addressed as hadoopstack.services.config.ec2_url for example
from hadoopstack.services import config
#from hadoopstack.services.config import *
#import config

def make_connection():
        url = config.ec2_url
        url_endpoint = url.split('/')[2]
        url_port = url.split(':')[2].split('/')[0]
        url_path = url.split(url_port)[1]    
	print url ,"  + ", url_endpoint, "+", url_port,"+",url_path
	print config.access_key
	print config.secret_key
        hs_region = EC2RegionInfo(name = "siel", endpoint = url_endpoint)
 	       
        conn=EC2Connection(aws_access_key_id=config.access_key,aws_secret_access_key=config.secret_key,is_secure=False,path=url_path,region=hs_region)
        return conn


#http://10.2.4.129:8773/services/cloud   +  10.2.4.129:8773 + 8773 + /services/cloud

def spawn_instances(conn, number, 
                    image_id = config.default_image_id, 
                    flavor = config.master_instance_flavor):
    conn.run_instances(image_id, int(number), int(number), None, None, flavor)


#def spawn_instances(conn, number, 
#                    image_id = "ami-0000001a", 
#                    flavor = "m1.tiny"):
#    conn.run_instances(image_id, int(number), int(number), None, None, flavor)
