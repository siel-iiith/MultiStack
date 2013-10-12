from multistack.main import app
from multistack import config

with app.app_context():
	config.set_conf()

app.run(host='0.0.0.0', port = 5000, debug = True, use_reloader = True)
