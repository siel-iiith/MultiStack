from flask import Blueprint,request,jsonify
import os
#from flask import request , Response
from urlparse import urlparse, parse_qs
import requests
import simplejson
#import json
from flask import jsonify



app_v1 = Blueprint('v1', __name__, url_prefix='/v1')

################custom modules to import

from connections import make_connection






def spawn_instances(image_id, number, keypair, sec_group, flavor):
	return conn.run_instances(default_image_id,int(default_min_vm),int(number),keypair,sec_group,flavor)








@app_v1.route('/',methods=['GET','POST'])
def version():
	if request.method == 'POST':
		data=request.json
		number_of_vms=int(data['cluster']['node-recipes']['tasktracker'])+int(data['cluster']['node-recipes']['jobtracker'])
		output = open("foo.txt", "a")
		output.write(str(data['cluster']))
		make_connection()
		output.write("number_of_vms"+str(number_of_vms))
		
			
		return jsonify(**request.json)    
	return "This is me here , v1"


