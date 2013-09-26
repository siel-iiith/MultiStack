from hadoopstack import config
from time import sleep
from multiprocessing import Process

import hadoopstack
import simplejson

from hadoopstack.dbOperations.db import flush_data_to_mongo
import hadoopstack.services.cluster as cluster
from bson import objectid

def create(data):

    flavor = ['m1.tiny', 'm1.small', 'm1.medium', 'm1.large', 'm1.xlarge']

    # Validation
    name = hadoopstack.main.mongo.db.job.find_one({'name': data['job']['name']})

    if name != None:
        return 0
    if 's3://' not in data['job']['input']:
        if 'swift://' not in data['job']['input']:
            return 0
    if 's3://' not in data['job']['output']: 
        if 'swift://' not in data['job']['output']:
            return 0
    if data['job']['master']['flavor'] not in flavor:
        return 0
    for slave in data['job']['slaves']:
        if slave['flavor'] not in flavor:
            return 0

    hadoopstack.main.mongo.db.job.insert(data)

    id_t = str(data['_id'])
    data['job']['id'] = id_t
    flush_data_to_mongo('job', data)

    create_ret = {}
    create_ret['job_id'] = id_t

    Process(target = cluster.create, args = (data,)).start()

    return create_ret

def delete(job_id):

    job = info(job_id)

    # TODO: Request Cluster API for Cluster Deletion

    print job['job']['status']
    if (
        job['job']['status'] != 'terminated' and
        job['job']['status'] != 'completed'
        ):
        
        cluster.delete(job_id)
        job['job']['status'] = 'terminated'
        flush_data_to_mongo('job', job)

        return ('Terminated Job', 200)

    else:
        return ("Job isn't running", 412)

def info(job_id):

    job_info = hadoopstack.main.mongo.db.job.find_one({"_id": objectid.ObjectId(job_id)})
    return job_info

def job_list():

    jobs_dict = {"jobs": []}
    for i in list(hadoopstack.main.mongo.db.job.find()):
        jobs_dict["jobs"].append(i['job'])

    return jobs_dict

def Scheduler(job_id):
   
    # A FiFo Scheduler implemented
    return
    for i in hadoopstack.main.mongo.db.job.find().sort("submission_time"):
        if i["_id"]!=objectid.ObjectId(job_id["job_id"]):
            while i["status"]!="completed":
                pass

