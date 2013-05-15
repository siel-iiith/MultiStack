from flask import Blueprint, request, jsonify
import os

from hadoopstack.services.cluster import make_connection
from hadoopstack.services.cluster import spawn_instances

app_v1 = Blueprint('v1', __name__, url_prefix='/v1')

@app_v1.route('/')
def version():
    return "v1 API. Jobs and clusters API are accessible at /jobs and /clusters respectively"

@app_v1.route('/clusters/', methods = ['GET','POST'])
def clusters():
    if request.method == 'POST':
        data = request.json
        number_of_vms = int(data['cluster']['node-recipes']['tasktracker']) + int(data['cluster']['node-recipes']['jobtracker'])
        output = open("foo.txt", "a")
        output.write(str(data['cluster']))
        conn=make_connection()
        spawn_instances(conn,number_of_vms)
        output.write("number_of_vms"+str(number_of_vms))
            
        return jsonify(**request.json)    
        
    return "To be implemented"


