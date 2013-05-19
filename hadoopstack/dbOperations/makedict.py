

def fetchDict(conn,allVMDetails):
	clusterDetails={}
	clusterDetails['VMids']=[i[0] for i in allVMDetails]
	clusterDetails['user']="penguinRaider" ############hardcoded for now will pull later after getting details      
	clusterDetails['userId']=[i.owner_id for i in conn.get_all_instances() ] ############not sure if this is to be implemented or the user so putting both for now
	clusterDetails['stack']="hadoop"       ############as per blueprint
	clusterDetails['created_at']=[i[1] for i in allVMDetails]
	clusterDetails['updated_at']="NA"
	clusterDetails['status']=[i[2] for i in allVMDetails]
	return clusterDetails

