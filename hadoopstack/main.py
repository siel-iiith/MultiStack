import os
from flask import Flask , request , Response
from .api.v1 import app_v1
from urlparse import urlparse, parse_qs
app = Flask(__name__)
app.register_blueprint(app_v1)
import requests
import simplejson
from flask import jsonify
del os.environ['http_proxy']


 
@app.route('/',methods=['GET', 'POST'])
def default():
	if request.method == 'POST':
		
		return jsonify(**request.json)

		#return "hello"	       	
		#r = requests.get("http://localhost:5000") 
		#c = r.content 
		#result = simplejson.loads(c)
		#return result
	#print parse_qs(urlparse("localhost:5000").query)
	return "Current API is v1 accessible on url prefix /v1"




if __name__ == '__main__':
#    app.debug = True
    app.run(host='0.0.0.0')



if not app.debug:
    import logging
    from logging import FileHandler
    file_handler = FileHandler("error.txt")
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)
