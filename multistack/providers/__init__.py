from flask import current_app

provider_map = {
	'ec2': ['multistack.providers.ec2', 'EC2Provider']
}

def get_cloud_provider(provider_name):
	module, provider = provider_map[provider_name]
	_mod = __import__(module, globals(), locals(), [provider])
	return getattr(_mod, provider)

def initiate_cloud(provider_name, job_name, credentials):
	cloud = get_cloud_provider(provider_name)
	current_app.cloud = cloud(job_name, credentials)
