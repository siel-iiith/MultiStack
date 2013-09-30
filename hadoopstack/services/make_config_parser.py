import ConfigParser

def configParserHelper(filename = "hadoopstack/testconfig.py"):
	####Default Call doesnot require filename If some other config file is desired \
	####change the name to something else
	
	Config = ConfigParser.ConfigParser()
	Config.read(filename)
	return Config
