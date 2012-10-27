from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import EC2RegionInfo

region_var = EC2RegionInfo(name="siel.openstack", endpoint="10.2.4.129:8773")
print region_var

#This a fixed image ID for our private cloud. Its ubuntu-12.04-amd64

default_image_id = "ami-00000010"

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
    
    @return: The connection descriptor.
    
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
                                 is_secure="false",
                                 path=url_path)
    return conn;

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
    
    
    
    key_pair = conn.create_key_pair("hadoopstack")
    key_pair.save("/tmp/HadoopStack")
    return True

def spawn_instances(number, flavor, keypair, region, image_id, sec_group):
    '''
    Function: spawn_instances(number, flavor)
    -----------------------------------
    This function spawns virtual machines.
    
    @param number: The number of virtual machines to boot.
    @param flavor: The flavor of virtual machine, e.g. - m1.small etc.
    @param keypair: SSH keypair to be associated with each instance.
    @param region: Region in which instance will be spawned.
    @param image: Image to be booted.
    @param sec_group: Security group the instances are going to be associated with.
    
    @return 
    
    '''
    
def create_sec_group():
    '''
    Function: create_sec_group()
    ---------------------------
    It creates a default "hadoopstack" security group for booting VMs.
    
    @return: id of the security group.
     
    '''
    list_sec_groups = conn.get_all_security_groups(["HadoopStack"])
    
    if len(list_sec_groups) > 0:
        return list_sec_groups[0].id
    
    sec_group = conn.create_security_group("HadoopStack",
                "Default security group for HadoopStack VMs")
    
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

def estimate_run_instances(input_size, deadline):
    '''
    Function: estimate_run_instances(conn_desc)
    -------------------------------------------
    This function estimates the number and flavor of instances based on the
    input size and deadline of the project.
        
    @return: 
    
    '''
    
    instance_flavor = "m1.small"
    instance_number = "2"

    
