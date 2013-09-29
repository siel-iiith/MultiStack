import hadoopstack
from multiprocessing import Process
from hadoopstack.services.make_config_parser import configParserHelper
Config = configParserHelper("hadoopstack/flavorConfig.py")
import hadoopstack.services.cluster as cluster

def scheduler(data,operation):
	if(operation == "create"):
		totalRAM,totalVCPU,totalInstance = calculateUsage(data,operation)
		cloudDic,decider = priorityCalculator(totalRAM,totalVCPU,totalInstance)
		if(decider == 1):
			hadoopstack.main.mongo.db.cloudDetails.save(cloudDic)

			if(cloudDic['name'] == "openStack"):
				print "Going to openStack"
				data['job']['provider'] = "openStack"
				Process(target = cluster.create, args = (data,"privateCloudConfig")).start()
				return 1
			else:
				print "Going to amazonAWS"
				data['job']['provider'] = "AWS"
				Process(target = cluster.create, args = (data,"publicCloudConfig")).start()
				return 1
		else:
		 	return 0

	elif(operation == "delete"):
		totalRAM,totalVCPU,totalInstance = calculateUsage(data,operation)
		cloudDic = hadoopstack.main.mongo.db.cloudDetails.find_one({'name':data['job']['provider']})
		cloudDic['ram'] +=totalRAM
		cloudDic['vcpu'] +=totalVCPU
		cloudDic['instance'] +=totalInstance
		hadoopstack.main.mongo.db.cloudDetails.save(cloudDic)


		print "deletion API called"	
	




def priorityCalculator(totalRAM,totalVCPU,totalInstance):
	for i in range(1,-1,-1):
		decider = 0
		cloudDic = hadoopstack.main.mongo.db.cloudDetails.find_one({"priority":i})
		cloudDic,decider = quotaCalculator(cloudDic,totalRAM,totalVCPU,totalInstance)
		if(decider == 1):
			return cloudDic,1
	
	return {},0

	pass



def quotaCalculator(cloudDic,totalRAM,totalVCPU,totalInstance):
	if(totalRAM<cloudDic['ram'] and totalVCPU<cloudDic['vcpu'] and totalInstance<cloudDic['instance']):
		cloudDic['ram'] -=totalRAM
		cloudDic['vcpu'] -=totalVCPU
		cloudDic['instance'] -=totalInstance
		return cloudDic,1
		print cloudDic
		print "can be done"
	





def calculateUsage(data,operation):
	totalVCPUs = 0
	totalRAM = 0
	totalInstance = 0
	master = data['job']['master']['flavor']
	totalRAM += int(Config.get(master,"ram"))
	totalVCPUs += int(Config.get(master,"vcpu"))
	totalInstance += 1
	print totalRAM,totalVCPUs	
	for slave in data['job']['slaves']:

		totalRAM += int(Config.get(slave['flavor'],"ram"))
		totalVCPUs += int(Config.get(slave['flavor'],"vcpu"))
		totalInstance += 1
		print totalRAM,totalVCPUs
	return totalRAM,totalVCPUs,totalInstance




