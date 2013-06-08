#labelList=lambda x: 

def preparePropertyFile(conn,currentReservationId):
	propertiesFile=open("properties","w")
	allIPs=[ i.ip_address for r in conn.get_all_instances() if r.id==currentReservationId for i in r.instances]
	allPrivateIPs=[ i.private_ip_address for r in conn.get_all_instances() if r.id==currentReservationId for i in r.instances]
	ipList=map(lambda x,y :(x,y) ,allIPs,allPrivateIPs) 
	labelList=map( lambda x : "slave" if (x[0]==x[1]) else "jobtracker"  ,   ipList)
	completeList=map(lambda x,y:(x,y) ,ipList,labelList)
	propertiesFile.write(str(allIPs))
	propertiesFile.write(str(allPrivateIPs))
	propertiesFile.write(str(ipList))
	propertiesFile.write(str(labelList))
	propertiesFile.write(str(completeList))
	propertiesFile.flush()
	print "hello"
