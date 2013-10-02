import ConfigParser

def config_parser(filename = "hadoopstack.conf.sample"):
	
	config = ConfigParser.ConfigParser()
	config.read(filename)
	return config
