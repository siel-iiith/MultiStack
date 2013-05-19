from flask import Blueprint, request, jsonify,current_app
from flask.ext.pymongo import PyMongo
from hadoopstack.services.cluster import make_connection
from hadoopstack.services.cluster import spawn_instances
from hadoopstack.dbOperations.db import getVMid
from hadoopstack.dbOperations.makedict import fetchDict
import simplejson

app_v1 = Blueprint('v1', __name__, url_prefix='/v1')
#from hadoopstack.main import mongo
#app_v1.config.from_object('config')
mongo = PyMongo()
clusterDetails={}
import json

@app_v1.route('/')
def version():
    return "v1 API. Jobs and clusters API are accessible at /jobs and \
    /clusters respectively"

@app_v1.route('/clusters/', methods = ['GET','POST'])
def clusters():
    if request.method == 'POST':
        data = request.json
	#mongo.db.cluster.insert(data)
        num_tt = int(data['cluster']['node-recipes']['tasktracker'])
        num_jt = int(data['cluster']['node-recipes']['jobtracker'])        
        num_vms = num_jt + num_tt
	foo = open("foo.txt", "a")
	#print "Name of the file: ", foo.name
	foo.write("hello there ")
	foo.flush() 
	foo.write(str(type(data)))
	foo.write(str(data))
	
	#j = { "name" : "mongo" }
	
        conn=make_connection()
        spawn_instances(conn,num_vms)
        allVMDetails=getVMid(conn)
	foo.write("yada yada yada")
	foo.write(str([i[0] for i in allVMDetails]))
	foo.write("yada yada yada")
	foo.flush() 
	clusterDetails=fetchDict(conn,allVMDetails)
	
	mongo.db.cluster.insert(clusterDetails)
#	clusterDetails['VMids']=[i[0] for i in allVMDetails]
#	clusterDetails['user']="penguinRaider" ############hardcoded for now will pull later after getting details	
#	clusterDetails['userId']=[i.owner_id for i in conn.get_all_instances() ] ############not sure if this is to be implemented or the user so putting both for now
#	clusterDetails['stack']="hadoop"       ############as per blueprint
#	clusterDetails['created_at']=[i[1] for i in allVMDetails]
#	clusterDetails['updated_at']="NA"
#	clusterDetails['status']=[i[2] for i in allVMDetails]
	id_t=str(clusterDetails['_id'])
	foo.write("sTr"+str(simplejson.dumps(id_t))+"sTr")
	clusterDetails['_id']=simplejson.dumps(id_t)	
	foo.write(str(clusterDetails))    
	foo.close()
	return jsonify(**clusterDetails)
        #return jsonify(**request.json)    
        
    return app_v1.name


