#!/usr/bin/python
from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import EC2RegionInfo
import urllib2
import os
proxy_handler = urllib2.ProxyHandler({})
opener = urllib2.build_opener(proxy_handler)
urllib2.urlopen('http://www.google.com')


del os.environ['http_proxy']



print "reached here "

url = 'http://10.2.4.129:8773/services/cloud'
apikey = 'trial123'
passx = 'trial123'
pathx='/services/Cloud'
hs_region = EC2RegionInfo(name="anythin", endpoint='10.2.4.129:8773')

conn=EC2Connection(aws_access_key_id=apikey, aws_secret_access_key=passx, is_secure=False, path=pathx, region=hs_region)





for i in reservations:
     for i in r.instances:
         i.id

print conn.get_all_images()
print "got here"
