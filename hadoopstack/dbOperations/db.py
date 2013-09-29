import os
import hadoopstack
from time import sleep

def get_resv_obj(conn, resv_id):
	'''
	Most of the object values have to be updated to get the most recent values.
	This function takes care of it. As of now, only updated reservation objects
	are required.

	@param resv_obj: Its the reservation object
	@return resv_obj

	'''

	for res in conn.get_all_instances():
		if res.id == resv_obj.id:
			return res

def update_private_ip_address(conn, data):

	for node in data['job']['nodes']:
		if node['private_ip_address'] is None:
			node_resv_obj = get_resv_obj(conn, node['reservation_id'])
			while node_resv_obj.private_ip_address is None:
				sleep(2)
				print "updating node {0} private ip address".format(node['id'])
				get_resv_obj(conn, node_resv_obj)

			node[private_ip_address] = node_resv_obj.private_ip_address
			flush_data_to_mongo('job', data)

def get_node_objects(conn, role, resv_id=None):

	nodes = list()
	for resv in conn.get_all_instances():
		if resv.id == resv_id:
			for instance in resv.instances:
				node = dict()
				node['id'] = instance.id
				node['private_ip_address'] = instance.private_ip_address
				node['reservation_id'] = resv_id
				node['role'] = role
				nodes.append(node)
	print nodes
	return nodes

def flush_data_to_mongo(db_name, data_dict):
	print data_dict
	if db_name == "job":
		hadoopstack.main.mongo.db.job.save(data_dict)

	if db_name == "job":
		hadoopstack.main.mongo.db.job.save(data_dict)
