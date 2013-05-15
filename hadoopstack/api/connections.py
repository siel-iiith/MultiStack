from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import EC2RegionInfo




def make_connection():
        url = 'http://10.2.4.129:8773/services/cloud'
        apikey = 'trial123'
        passx = 'trial123'
        pathx='/services/Cloud'
        hs_region = EC2RegionInfo(name="anythin", endpoint='10.2.4.129:8773')
        conn=EC2Connection(aws_access_key_id=apikey, aws_secret_access_key=passx, is_secure=False, path=pathx, region=hs_region)

