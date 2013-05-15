default_image_id = "ami-0000001a"
default_min_vm = 1
master_instance_flavor = "m1.medium"
from connections import make_connection

def spawn_instances(conn, number=default_min_vm,image_id=default_image_id, flavor=master_instance_flavor):
	conn.run_instances(default_image_id,int(default_min_vm),int(number),None,None,flavor)



