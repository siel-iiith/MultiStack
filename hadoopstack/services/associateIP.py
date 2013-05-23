from hadoopstack.dbOperations.db import getVMid
import time
#time.sleep(secs)

def associatePublicIp(conn,reserveId):
	listDetails=getVMid(conn,reserveId)
	
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
		if(not i.instance_id):
			i.associate(str(listDetails[0][0].split(":")[1]))
			break
	foo.write(str(ipPool))

	#allEle[
	#for r in conn.get_all_addresses():
		
