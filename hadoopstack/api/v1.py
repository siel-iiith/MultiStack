from flask import Blueprint,request,jsonify
import os
#from flask import request , Response
from urlparse import urlparse, parse_qs

import requests
import simplejson
#import json
from flask import jsonify
app_v1 = Blueprint('v1', __name__, url_prefix='/v1')

@app_v1.route('/',methods=['GET','POST'])
def version():
	if request.method == 'POST':
		data=request.raw_post_data
		
		return jsonify(**request.json)    
	return "This is me here , v1"


