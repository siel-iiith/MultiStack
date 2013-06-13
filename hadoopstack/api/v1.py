from flask import Blueprint, request, jsonify,current_app
from flask.ext.pymongo import PyMongo

from hadoopstack.services.cluster import make_connection
from hadoopstack.services.cluster import spawn_instances

from hadoopstack.services import job
from hadoopstack.services import cluster

from hadoopstack.dbOperations.db import getVMid
from hadoopstack.dbOperations.makedict import fetchDict
#<<<<<<< HEAD
from hadoopstack.services.associateIP import associatePublicIp
from hadoopstack.services.connectToMaster import connectMaster
#from hadoopstack.services.prepareProperties import preparePropertyFile
from hadoopstack.services.prepareProperties import preparePropertyFile
import os
import simplejson
import json
import hadoopstack.main






app_v1 = Blueprint('v1', __name__, url_prefix='/v1')
#from hadoopstack.main import mongo
#app_v1.config.from_object('config')
#mongo = PyMongo()
clusterDetails={}
POSTout={}


@app_v1.route('/',methods = ['GET','POST'])
def version():
    '''
        GET request of the cluster API
    '''
    if request.method == 'POST':
        cursor=hadoopstack.main.mongo.db.cluster.find()
        allEle=[]
        for obj in hadoopstack.main.mongo.db.cluster.find(): allEle.append(obj)
        objToReturn={}
        objToReturn['cluster']=allEle;
        xxx=allTuples=[(objToReturn[i]) for i in objToReturn]
        #yyy=xxx[0][0]['_id']
        allIds=[  (str(ids['_id'])) for i in allTuples for ids in i]
        for i in xrange(0,len(allIds)):
            allTuples[0][i]['_id']=allIds[i]
        #[ allTuples[i][0]['_id']=allIds[i]		for i in xrange(0,len(allIds))]
        #objToReturn['cluster']=map(lambda x,y:    ,allTuples,allIds)
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
        PUT request of cluster API
    '''
    if request.method == 'POST':
        data = request.json
        # This inserts the complete json post data in Mongo
        #inserting json  to the mongoDB
        hadoopstack.main.mongo.db.clustersRawData.insert(data)
        conn,reservationId = cluster.setup(data)
        reserveId = [ i.id for i in reservationId]
        allVMDetails=getVMid(conn,reserveId)
        recipeList=[]
        num_tt = int(data['cluster']['node-recipes']['tasktracker'])
        num_jt = int(data['cluster']['node-recipes']['jobtracker'])       
        [  recipeList.append("jobtracker")   for i in xrange(0,num_jt)]
        [  recipeList.append("tasktracker")   for i in xrange(0,num_tt)]
        clusterDetails=fetchDict(conn,allVMDetails,recipeList,reserveId)
        hadoopstack.main.mongo.db.cluster.insert(clusterDetails)
        #jobreserveId=reserveId[0]
        masterIp=associatePublicIp(conn,reserveId)
        preparePropertyFile(conn,reserveId)
        #connectMaster(masterIp,conn)
        #id_t=str(clusterDetails['_id'])
        #clusterDetails['_id']=simplejson.dumps(id_t)	
        #POSTout['CID']=id_t
        #return jsonify(**POSTout)

 
        # Need to return an ID after sucessful completion
        #return "Cluster Spawned\n"
    return "To Be Implemented"
    #return app_v1.name
