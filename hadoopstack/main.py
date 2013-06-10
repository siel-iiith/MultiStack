import os
from flask import Flask
from hadoopstack.api.v1 import app_v1
from flask.ext.pymongo import PyMongo
sahni = 1

app = Flask(__name__)
app.config.from_object('hadoopstack.config')

app.register_blueprint(app_v1)

mongo = PyMongo(app)

@app.route('/')
def default():
    return app.name + " running and Current API is v1 accessible on url prefix /v1/"

if __name__ == '__main__':
    app.run(host='0.0.0.0')

if not app.debug:
    import logging
    from logging import FileHandler
    file_handler = FileHandler("error.txt")
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)
