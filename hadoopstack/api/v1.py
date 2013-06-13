from flask import Blueprint, request, jsonify,current_app
from flask.ext.pymongo import PyMongo

from hadoopstack.services.cluster import make_connection
from hadoopstack.services.cluster import spawn_instances

from hadoopstack.services import job
from hadoopstack.services import cluster

from hadoopstack.dbOperations.db import getVMid
from hadoopstack.dbOperations.makedict import fetchDict
from hadoopstack.services.associateIP import associatePublicIp
from hadoopstack.services.connectToMaster import connectMaster
from hadoopstack.services.prepareProperties import preparePropertyFile

import os
import simplejson
import json
import hadoopstack.main

app_v1 = Blueprint('v1', __name__, url_prefix='/v1')
clusterDetails={}
POSTout={}

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

@app_v1.route('/jobs/', methods=['GET', 'POST'])
def jobs():
    if request.method == 'GET':
        return ' '.join(job.jobs_list)

    elif request.method == 'POST':
        return "To Be Implemented"

@app_v1.route('/clusters/', methods = ['GET','POST'])
def clusters():
    '''
        Cluster API
    '''
    if request.method == 'POST':
        data = request.json
        
        # This inserts the complete json post data in Mongo
        # We need to create an api_check() filter before inserting
        hadoopstack.main.mongo.db.clustersRawData.insert(data)
        conn,reservationId = cluster.setup(data)
        reserveId = [ i.id for i in reservationId]
        allVMDetails = getVMid(conn,reserveId)
        recipeList = []
        num_tt = int(data['cluster']['node-recipes']['tasktracker'])
        num_jt = int(data['cluster']['node-recipes']['jobtracker'])       
        [recipeList.append("jobtracker")    for i in xrange(0,num_jt)]
        [recipeList.append("tasktracker")   for i in xrange(0,num_tt)]
        clusterDetails = fetchDict(conn, allVMDetails, recipeList, reserveId)
        hadoopstack.main.mongo.db.cluster.insert(clusterDetails)
        
        masterIp = associatePublicIp(conn,reserveId)
        preparePropertyFile(conn,reserveId)
        
        id_t = str(clusterDetails['_id'])
        clusterDetails['_id'] = simplejson.dumps(id_t)	
        POSTout['CID'] = id_t
        return jsonify(**POSTout)

    return "To Be Implemented"