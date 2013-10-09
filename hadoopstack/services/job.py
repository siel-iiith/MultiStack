from multiprocessing import Process
from time import sleep
import logging
import simplejson

from flask import make_response
from flask import jsonify
from flask import current_app

import hadoopstack
from hadoopstack.dbOperations.db import flush_data_to_mongo
from hadoopstack.log import set_prefixed_format
from hadoopstack.scheduler.scheduler import schedule
import hadoopstack.services.cluster as cluster

from bson import objectid

def create(data):
    # Validation

    validation_result = validate(data)
    create_ret = dict()

    if validation_result != True:
        return validation_result

    hadoopstack.main.mongo.db.job.insert(data)
    id_t = str(data['_id'])
    data['job']['id'] = id_t
    flush_data_to_mongo('job', data)

    set_prefixed_format(id_t)

    if schedule(data, 'create'):
        create_ret['job_id'] = id_t
        return make_response(jsonify(**create_ret), 202)
    else:
        create_ret['error'] = "job_init_failed"
        return make_response(jsonify(**create_ret), 500)

    return make_response(jsonify(**create_ret), 202)

def validate(data):

    flavor = ['t1.micro', 'm1.small', 'm1.medium', 'm1.large', 'm1.xlarge']

    existing_job = hadoopstack.main.mongo.db.job.find_one({'job.name': data['job']['name']})

    if existing_job != None:
        return make_response("JOB_ALREADY_EXISTS", 400)

    if 's3://' not in data['job']['input']:
        if 'swift://' not in data['job']['input']:
            return make_response("INVALID_INPUT_LOCATION", 400 )

    if 's3://' not in data['job']['output']: 
        if 'swift://' not in data['job']['output']:
            return make_response("INVALID_OUTPUT_LOCATION", 400)

    if data['job']['master']['flavor'] not in flavor:
        return make_response("FLAVOR_NOT_FOUND", 400)

    for slave in data['job']['slaves']:
        if slave['flavor'] not in flavor:
            return make_response("FLAVOR_NOT_FOUND", 400)

    return True

def delete(job_id):

    set_prefixed_format(job_id)

    if info(job_id)[0]:
        job = info(job_id)[1]
    else:
        return make_response("JOB_NOT_FOUND", 412)

    if schedule(job, "delete"):
        return make_response('', 204)

    else:
        return make_response('JOB_TERMINATION_FAILED', 500)

def info(job_id):

    try:
        job_info = hadoopstack.main.mongo.db.job.find_one({"_id": objectid.ObjectId(job_id)})
        job_info.pop('_id')
        return True, job_info

    except:
        return False, make_response("JOB_NOT_FOUND", 412)

def job_list():

    jobs_dict = {"jobs": []}
    for i in list(hadoopstack.main.mongo.db.job.find()):
        jobs_dict["jobs"].append(i['job'])

    return jobs_dict

def add(data, job_id):

    data['id'] = job_id
    set_prefixed_format(job_id)
    if schedule(data, "add"):
        return make_response('', 202)

def remove(data, job_id):

    data['id'] = job_id
    set_prefixed_format(job_id)
    if schedule(data, "remove"):
        return make_response('', 202)
