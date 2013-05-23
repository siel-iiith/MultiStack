from flask import Blueprint, request, jsonify,current_app
from flask.ext.pymongo import PyMongo
from hadoopstack.services.cluster import make_connection
from hadoopstack.services.cluster import spawn_instances
from hadoopstack.dbOperations.db import getVMid
from hadoopstack.dbOperations.makedict import fetchDict
from hadoopstack.services.associateIP import associatePublicIp
import simplejson

app_v1 = Blueprint('v1', __name__, url_prefix='/v1')
#from hadoopstack.main import mongo
#app_v1.config.from_object('config')
mongo = PyMongo()
clusterDetails={}
POSTout={}
import json

@app_v1.route('/',methods = ['GET','POST'])
def version():
    '''
	GET request of the cluster API
    '''
    if request.method == 'POST':
 		cursor=mongo.db.cluster.find()
    		foo = open("foo.txt", "a")
		foo.write("hello there ")
    		foo.flush() 
    		foo.write(str(type(cursor)))
    		foo.write(str(cursor))
		foo.write(str(cursor.__dict__))
		allEle=[]
		
		for obj in mongo.db.cluster.find(): allEle.append(obj)
		
		objToReturn={}
		objToReturn['cluster']=allEle;
		foo.write("objetoReturn\n\n")
		foo.write(str(objToReturn))
		foo.write("\n\n\n");
		xxx=allTuples=[(objToReturn[i]) for i in objToReturn]
		#yyy=xxx[0][0]['_id']
		allIds=[  (str(ids['_id'])) for i in allTuples for ids in i]
		foo.write("allid\n")
		foo.write(str(allIds))
		foo.write("\n\n\n\n")
		foo.write("allTuples\n")
		foo.write(str(allTuples))
		foo.write("\n\n\n\n")
	 	#foo.write(str(allTuples[0][1]))
		
		foo.flush() 	
	
		for i in xrange(0,len(allIds)):
			allTuples[0][i]['_id']=allIds[i]
		#[ allTuples[i][0]['_id']=allIds[i]		for i in xrange(0,len(allIds))]

		#objToReturn['cluster']=map(lambda x,y:    ,allTuples,allIds)
		
		foo.write("ahdjhjshjhjfsdhjfsfsdhksd shjhfjghsdjgsdfjgsjfghsfghfdghgsdhgsdhgsdfhgfsdghfsd")
		#foo.write(str(xxx))
		foo.write("done done done done")
		#foo.write(str(yyy))
		foo.write("next to print")
		foo.write(str(allIds))
		foo.write("hence the list")
		foo.write(str(objToReturn))
		#for i in objToReturn:
		#	 for  in i:
		#		foo.write(i)
		return jsonify(**objToReturn)


    return "v1 API. Jobs and clusters API are accessible at /jobs and \
    /clusters respectively"

@app_v1.route('/clusters/', methods = ['GET','POST'])
def clusters():
    '''
	PUT request of cluster API

    '''
    if request.method == 'POST':
        data = request.json
	#mongo.db.cluster.insert(data)
        recipeList=[]
	num_tt = int(data['cluster']['node-recipes']['tasktracker'])
        num_jt = int(data['cluster']['node-recipes']['jobtracker'])       
	[  recipeList.append("jobtracker")   for i in xrange(0,num_jt)]
	[  recipeList.append("tasktracker")   for i in xrange(0,num_tt)]
	

 
        num_vms = num_jt + num_tt
	foo = open("foo.txt", "a")
	#print "Name of the file: ", foo.name
	foo.write("hello there ")
	foo.flush() 
	foo.write(str(type(data)))
	foo.write(str(data))
	
	#j = { "name" : "mongo" }
	
        conn=make_connection()
        reservationId=spawn_instances(conn,num_vms)
	reserveId=reservationId.id
        allVMDetails=getVMid(conn,reserveId)
	foo.write("yada yada yada")
	foo.write(str([i[0] for i in allVMDetails]))
	foo.write("yada yada yada")
	foo.flush() 
	clusterDetails=fetchDict(conn,allVMDetails,recipeList,reserveId)
	
	mongo.db.cluster.insert(clusterDetails)
#	clusterDetails['VMids']=[i[0] for i in allVMDetails]
#	clusterDetails['user']="penguinRaider" ############hardcoded for now will pull later after getting details	
#	clusterDetails['userId']=[i.owner_id for i in conn.get_all_instances() ] ############not sure if this is to be implemented or the user so putting both for now
#	clusterDetails['stack']="hadoop"       ############as per blueprint
#	clusterDetails['created_at']=[i[1] for i in allVMDetails]
#	clusterDetails['updated_at']="NA"
#	clusterDetails['status']=[i[2] for i in allVMDetails]
	associatePublicIp(conn,reserveId)
		
	id_t=str(clusterDetails['_id'])
	foo.write("sTr"+str(simplejson.dumps(id_t))+"sTr")
	clusterDetails['_id']=simplejson.dumps(id_t)	
	POSTout['CID']=id_t
	foo.write(str(clusterDetails))    
	foo.close()
	return jsonify(**POSTout)
        #return jsonify(**request.json)    
        
    return app_v1.name


