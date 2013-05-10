from flask import Blueprint

app_v1 = Blueprint('v1', __name__)

@app_v1.route('/')
def version():
    return "v1"