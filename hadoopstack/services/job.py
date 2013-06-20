from hadoopstack import config
from time import sleep

import hadoopstack
import simplejson

from hadoopstack.dbOperations.makedict import jobDict

from bson import objectid

jobs_list = []

def create(data):

    jobDetails = jobDict(data)
    hadoopstack.main.mongo.db.job.insert(jobDetails)

    #print jobDetails
    id_t = str(jobDetails['_id'])
    jobDetails['_id'] = simplejson.dumps(id_t)

    jobs_list.append(jobDetails['name'])   
    create_ret = {}
    create_ret['job_id'] = id_t
    return create_ret


def delete(job_id):

    job_info = hadoopstack.main.mongo.db.job.find({"_id": objectid.ObjectId(job_id)})[0]

    # Not Actually deleted the job from the Database, setting the status to DELETED
    job_info['status'] = "deleted"

    return ('Deleted Job', 200)
