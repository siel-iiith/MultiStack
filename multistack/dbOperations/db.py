import os
from time import sleep

import multistack

def flush_data_to_mongo(db_name, data_dict):
	if db_name == 'job':
		multistack.main.mongo.db.job.save(data_dict)

	if db_name == 'conf':
		multistack.main.mongo.db.conf.save(data_dict)
