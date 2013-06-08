from hadoopstack.dbOperations.db import getVMid
import time
#time.sleep(secs)
import os
def associatePublicIp(conn,reserveId):
#	proxy=os.environ['http_proxy']
#	del   os.environ['http_proxy']
#	os.environ['http_proxy']=proxy

	listDetails=getVMid(conn,reserveId)
#	del   os.environ['http_proxy']

	ipToReturn=""
        #for obj in mongo.db.cluster.find(): allEle.append(obj)
	foo=open("ru.txt","w")
	foo.write(str(listDetails))
	foo.write(str(listDetails[0][0].split(":")[1]))
	foo.write("hello")
	ipPool=[     i.public_ip         for i in conn.get_all_addresses()]
	foo.write("check")
	time.sleep(5)
	foo.write(str(listDetails[0][0].split(":")[1]))
	foo.flush()	
	for i in conn.get_all_addresses():
		print i.public_ip
		if(not i.instance_id):
			print "i getting associate is "
			print i.public_ip
			i.associate(str(listDetails[0][0].split(":")[1]))
			ipToReturn=str(i.public_ip)
			break
	foo.write(str(ipPool))
#os.environ['http_proxy']=proxy

	return ipToReturn
	#allEle[
	#for r in conn.get_all_addresses():
		
