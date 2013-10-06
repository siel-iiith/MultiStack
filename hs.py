from hadoopstack.main import app
from hadoopstack import config

with app.app_context():
	config.set_conf()

app.run(host='0.0.0.0', port = 5000, debug = True, use_reloader = True)
