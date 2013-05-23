from hadoopstack.dbOperations.db import getVMid


def associatePublicIp(conn,reserveId):
	listDetails=getVMid(conn,reserveId)

        #for obj in mongo.db.cluster.find(): allEle.append(obj)
	foo=open("ru.txt","w")
	foo.write(str(listDetails))
	#allEle[
	#for r in conn.get_all_addresses():
		
