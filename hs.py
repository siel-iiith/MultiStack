from hadoopstack.main import app
from hadoopstack.services.make_config_parser import configParserHelper
Config = configParserHelper("hadoopstack/testconfig.py")
from hadoopstack import main

with app.app_context():
	amazonPriority = Config.get("PriorityOrder","AWS")
	openStackPriority = Config.get("PriorityOrder","openStack")
	openStackInstance = { i[0]:int(i[1]) for i in Config.items("usageQuotaOpenStack")}
	amazonAWSInstance = { i[0]:int(i[1]) for i in Config.items("usageQuotaAmazonAWS")}
	openStackInstance['name'] = "openStack"
	amazonAWSInstance['name'] = "AWS"
	openStackInstance['priority'] = int(openStackPriority)
	amazonAWSInstance['priority'] = int(amazonPriority)
	main.mongo.db.cloudDetails.save(openStackInstance)
	main.mongo.db.cloudDetails.save(amazonAWSInstance)


	print openStackInstance
	print amazonAWSInstance



app.run(host='0.0.0.0',port = 5000, debug=True,use_reloader=False)
