from flask import Blueprint, Flask, request, session, url_for, redirect, jsonify

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
        return job.create(data)

@app_v1.route('/jobs/<job_id>', methods = ['GET','DELETE'])
def job_api(job_id):

    if request.method == "GET":
        return jsonify(job.info(job_id))

    elif request.method == "DELETE":
        return job.delete(job_id)

@app_v1.route('/jobs/<job_id>/add', methods = ['POST'])
def add(job_id):
    if request.method == "POST":
        return job.add(request.json, job_id)

@app_v1.route('/jobs/<job_id>/rm', methods = ['POST'])
def remove(job_id):
    if request.method == "POST":
        return job.remove(request.json, job_id)
