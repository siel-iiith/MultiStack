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
        import pdb;pdb.set_trace()
        if not request.form['name']:
            flash('Please enter the name')
            return redirect(url_for(".create_job"))
        import pdb;pdb.set_trace()
        if not request.form['des']:
            request.form['des'] = u'Test'
        if not request.form['jar']:
            flash('Please enter the jar file')
            return redirect(url_for(".create_job"))
        import pdb;pdb.set_trace()
        if not request.form['mc']:
            flash('Please enter the Main Class')
            return redirect(url_for(".create_job"))
        import pdb;pdb.set_trace()
        if not request.form['ip']:
            flash('Please enter the Input Path')
            return redirect(url_for(".create_job"))
        import pdb;pdb.set_trace()
        if not request.form['op']:
            flash('Please enter the Output Path')
            return redirect(url_for(".create_job"))
        import pdb;pdb.set_trace()
        if not request.form['mf']:
            flash('Please enter the Master Flavor')
            return redirect(url_for(".create_job"))
        import pdb;pdb.set_trace()
        if not request.form['mi']:
            default = u'1'
        else:
            default = request.form['mi']
        if not request.form['sf']:
            flash('Please enter the Slave Flavor')
            return redirect(url_for(".create_job"))
        import pdb;pdb.set_trace()
        if not request.form['slit']:
           flash('Please enter the Slave Instance')
           return redirect(url_for(".create_job"))
        if not request.form['dead']:
            request.form['dead'] = u'Test'
        if not request.form['so']:
            request.form['so'] = u'Special'
        data = {}
        import pdb;pdb.set_trace()
        data['jobs'] = {"name": request.form["name"], "description": request.form["des"] , "jar": request.form["jar"], \
                        "MainClass": request.form["mc"], "Input Path": request.form["ip"], "Output Path": request.form["op"], \
                        "master": {"masterFlavor": request.form["mf"], "masterInstance": default}, \
                        "slave": {"slaveFlavor": request.form["sf"], "slaveInstance": request.form["slit"]}, \
                        "deadline": request.form["dead"], "Special Option": request.form["so"]}
        import pdb;pdb.set_trace()
        print data
        job_id = job.create(data)
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
#        return jsonify(**job_id)
        return render_template("list_jobs.html",joblist=job.job_list()['jobs'])

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

