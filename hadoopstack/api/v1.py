from flask import Blueprint, request, jsonify,current_app
from flask.ext.pymongo import PyMongo

from hadoopstack.services import job
from hadoopstack.services import cluster

import simplejson
import json
import hadoopstack.main

app_v1 = Blueprint('v1', __name__, url_prefix='/v1')

@app_v1.route('/',methods = ['GET','POST'])
def version():
    '''
        GET request of the cluster API
    '''
    if request.method == 'POST':
        cursor = hadoopstack.main.mongo.db.cluster.find()
        allEle = []
        for obj in hadoopstack.main.mongo.db.cluster.find():
            allEle.append(obj)
        objToReturn = {}
        objToReturn['cluster'] = allEle;
        allTuples = [(objToReturn[i]) for i in objToReturn]
        allIds = [(str(ids['_id'])) for i in allTuples for ids in i]
        for i in xrange(0,len(allIds)):
            allTuples[0][i]['_id'] = allIds[i]
        return jsonify(**objToReturn)


    return "v1 API. Jobs and clusters API are accessible at /jobs and \
    /clusters respectively"

@app_v1.route('/jobs', methods=['GET', 'POST'])
def jobs_api():
    '''
        Jobs API
    '''
    if request.method == 'GET':
        get_output = []
        for i in list(hadoopstack.main.mongo.db.job.find()):
            get_output.append(i["name"])

        return "\n".join(get_output)

    elif request.method == 'POST':
        data = request.json
        job_id = job.create(data)
        return jsonify(**job_id)

@app_v1.route('/jobs/<job_id>', methods = ['GET','DELETE'])
def job_api(job_id):
    if request.method == 'GET':
        get_output = []
        for i in list(hadoopstack.main.mongo.db.job.find()):
            get_output.append(i["name"])

        return "\n".join(get_output)

    elif request.method == "DELETE":
        return job.delete(job_id)

@app_v1.route('/clusters', methods = ['GET','POST'])
def clusters_api():
    '''
        Cluster API
    '''
    if request.method == 'POST':
        data = request.json
        cid = cluster.create(data)
        return jsonify(**cid)

    return "To Be Implemented"

@app_v1.route('/clusters/<cluster_id>', methods = ['GET','DELETE'])
def cluster_api(cluster_id):
    if request.method == "DELETE":
        return cluster.delete(cluster_id)

    return "To Be Implemented"

