from flask import Flask
from .api.v1 import app_v1

app = Flask(__name__)
app.register_blueprint(app_v1)

if __name__ == '__main__':
    app.run(host='0.0.0.0')