from flask import Blueprint, Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, jsonify
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

@app_v1.route('/jobs', methods=['GET', 'POST'])
def jobs_api():
    '''
        Jobs API
    '''
    
    if request.method == 'GET':
        return jsonify(**job.job_list())

    elif request.method == 'POST':
        data = request.json
        job_id = job.create(data)

        if job_id == 0:
            return "Error: Invalid input"
        
        return jsonify(**job_id)

@app_v1.route('/jobs/<job_id>', methods = ['GET','DELETE'])
def job_api(job_id):

    if request.method == "GET":
        return jsonify(job.info(job_id))
        
    elif request.method == "DELETE":
        return job.delete(job_id)

@app_v1.route('/clusters', methods = ['GET','POST','PUT'])
def clusters_api():
    '''
        Cluster API
    '''
    if request.method == 'GET':
        return jsonify(**cluster.list_clusters())

    if request.method == 'POST':
        data = request.json
        cid = cluster.create(data)
        return jsonify(**cid)

    if request.method == 'PUT':
        data = request.json

    return "To Be Implemented"

@app_v1.route('/clusters/<cluster_id>/add', methods = ['POST'])
def add(cluster_id):
    '''
    API to add noe to a cluster
    '''

    data = request.json
    cluster.add_node(data, cluster_id)
    return

@app_v1.route('/clusters/<cluster_id>', methods = ['GET','DELETE'])
def cluster_api(cluster_id):
    if request.method == "DELETE":
        return cluster.delete(cluster_id)

    return "To Be Implemented"

