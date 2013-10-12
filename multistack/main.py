import logging

from flask import Flask
from flask.ext.pymongo import PyMongo

from multistack import config
from multistack.api.v1 import app_v1

app = Flask(__name__)
configparser = config.config_parser()
app.config['MONGO_HOST'] = configparser.get('flask', 'MONGO_HOST')
app.config['MONGO_DBNAME'] = configparser.get('flask', 'MONGO_DBNAME')
app.config['DEBUG'] = True

if configparser.has_option('DEFAULT', 'syslog_server_ip'):
	app.syslog_address = (configparser.get('DEFAULT', 'syslog_server_ip'),
						int(configparser.get('DEFAULT', 'syslog_server_port')))
else:
	app.syslog_address = '/dev/log'

app.register_blueprint(app_v1)

mongo = PyMongo(app)

handler = logging.handlers.SysLogHandler(address = app.syslog_address)
app.logger.addHandler(handler)

@app.route('/')
def default():
    return app.name + " running and Current API is v1 accessible on url prefix /v1/"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
