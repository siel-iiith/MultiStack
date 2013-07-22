from flask import Blueprint, Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, jsonify
from hadoopstack.services import job
from hadoopstack.services import cluster

import simplejson
import json
import hadoopstack.main
import requests
import os
from bson import objectid

app_v1 = Blueprint('v1', __name__, url_prefix='/v1')

@app_v1.route('/')
def version():
    '''
        GET request of the cluster API
    '''

    return render_template("welcome.html")

@app_v1.route('/create_job', methods=['GET'])
def create_job():
    return render_template("create_job.html")

@app_v1.route('/jobs', methods=['GET', 'POST'])
def jobs_api():
    '''
        Jobs API
    '''
    
    if request.method == 'GET':
        print job.job_list()['jobs']
        return render_template("list_jobs.html",joblist=job.job_list()['jobs'])

    elif request.method == 'POST':
        data = request.json
        print data
        job_id = job.create(data)
#print job_id
        a = hadoopstack.main.mongo.db.job.find_one({'_id': objectid.ObjectId(job_id['job_id'])})
        a['status'] = 'waiting'
        hadoopstack.main.mongo.db.job.save(a)
        # Calling the Scheduler
        job.Scheduler(job_id)
        # @Todo: To work with threads/ to multiple request to enable this: 
#       payload = {'cluster':{'name':str(int(random.random()*10000)), 'node-recipes': {'tasktracker':2,'jobtracker':1},'image-id':'ubuntu-12.04-amd64.img'}} 
#       headers = {'content-type': 'application/json', 'accept': 'application/json'}

#       r = requests.post("http://127.0.0.1:5000/v1/clusters", data=json.dumps(payload), headers=headers)
        
        # @Todo: To associate the cluster id to the job.  
        a['status'] = "completed"
        hadoopstack.main.mongo.db.job.save(a)
        return jsonify(**job_id)

@app_v1.route('/jobs/<job_id>', methods = ['GET','DELETE'])
def job_api(job_id):

    if request.method == "GET":        
        return jsonify(job.info(job_id))
        
    elif request.method == "DELETE":
        return job.delete(job_id)

@app_v1.route('/clusters', methods = ['GET','POST'])
def clusters_api():
    '''
        Cluster API
    '''
    if request.method == 'GET':
        print cluster.cluster_list()['clusters']
        return render_template("list_clusters.html",clusterlist=cluster.cluster_list()['clusters'])
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

