from hadoopstack import config
from time import sleep

import hadoopstack
import simplejson

from hadoopstack.dbOperations.makedict import jobDict

from bson import objectid

jobs_list = ['job1', 'job2']

def create(data):

    jobDetails = jobDict(data)
    hadoopstack.main.mongo.db.job.insert(jobDetails)
    id_t = str(jobDetails['_id'])
    jobDetails['_id'] = simplejson.dumps(id_t)
    create_ret = {}
    create_ret['job_id'] = id_t
    return create_ret
