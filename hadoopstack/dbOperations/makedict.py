import simplejson

def fetchDict(conn,allVMDetails,recipeList):
	clusterDetails={}
	VMIdList=[]
	#for i in xrange(0,len(allVMDetails)):
	#VMMap=map(lambda x,y :(x,y),[i[0] for i in allVMDetails],recipeList)
	VMIdList=[{"id":i[0],"role":i[1]} for i in map(lambda x,y :(x,y),[i[0] for i in allVMDetails],recipeList) ]
	#clusterDetails['VMids']=simplejson.dumps([i[0] for i in allVMDetails])
	clusterDetails['VMids']=simplejson.dumps(VMIdList)
	


	clusterDetails['user']="penguinRaider" ############hardcoded for now will pull later after getting details      
	clusterDetails['userId']=simplejson.dumps([i.owner_id for i in conn.get_all_instances() ]) ############not sure if this is to be implemented or the user so putting both for now
	clusterDetails['stack']="hadoop"       ############as per blueprint
	clusterDetails['created_at']=simplejson.dumps([i[1] for i in allVMDetails])
	clusterDetails['updated_at']="NA"
	clusterDetails['status']=simplejson.dumps([i[2] for i in allVMDetails])
	return clusterDetails

