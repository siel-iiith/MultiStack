from hadoopstack import config
from time import sleep

import hadoopstack
import simplejson

from hadoopstack.dbOperations.makedict import jobDict

from bson import objectid

def create(data):

    jobDetails = jobDict(data)
    hadoopstack.main.mongo.db.job.insert(jobDetails)
    id_t = str(jobDetails['_id'])
    create_ret = {}
    create_ret['job_id'] = id_t
    return create_ret

def delete(job_id):

    job_info = info(job_id)['jobs']

    # TODO: Request Cluster API for Cluster Deletion

    print job_info['status']
    if ( 
        job_info['status'] != 'deleted' and
        job_info['status'] != 'completed'
        ):
        # Not Actually deleted the job from the Database, setting the status to DELETED
        hadoopstack.main.mongo.db.job.update({"_id": objectid.ObjectId(job_id)},
                                             { "$set": { 'status' : 'deleted' }})
        return ('Deleted Job', 200)

    else:
        return ("Job isn't running", 412)

def info(job_id):

    job_info = hadoopstack.main.mongo.db.job.find_one({"_id": objectid.ObjectId(job_id)})
    job_info["_id"] = job_id
    job_dict = {"jobs": job_info}  
    return job_dict

def job_list():

    jobs_dict = {"jobs": []}
    for i in list(hadoopstack.main.mongo.db.job.find()):
        i["_id"] = str(i["_id"])
        jobs_dict["jobs"].append(i)

    return jobs_dict

def Scheduler(job_id):
   
    # A FiFo Scheduler implemented
    return
    for i in hadoopstack.main.mongo.db.job.find().sort("submission_time"):
        if i["_id"]!=objectid.ObjectId(job_id["job_id"]):
            while i["status"]!="completed":
                pass

