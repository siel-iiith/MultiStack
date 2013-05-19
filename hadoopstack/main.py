import os
from flask import Flask
from hadoopstack.api.v1 import app_v1
from hadoopstack.api.v1 import mongo
from flask.ext.pymongo import PyMongo
#from hadoopstack.main import mongo
#from mongokit import Connection,Document

app = Flask(__name__)
#app.config['MONGO_DBNAME']="clusterDB"
app.config.from_object('config')


app.register_blueprint(app_v1)
#mongo = PyMongo(app)
mongo.init_app(app,config_prefix="MONGO")

@app.route('/')
def default():
#    return app.name
    return app.name + " running and Current API is v1 accessible on url prefix /v1/"

if __name__ == '__main__':
    app.run(host='0.0.0.0')

if not app.debug:
    import logging
    from logging import FileHandler
    file_handler = FileHandler("error.txt")
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)
