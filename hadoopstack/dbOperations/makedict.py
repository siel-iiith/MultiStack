import simplejson
import os

def fetchDict(conn,allVMDetails,recipeList,reserveId):
    
    clusterDetails={}

    VMIdList=[{'id':i[0],'role':i[1]} for i in map(lambda x,y :(x,y),[instance[0] for instance in allVMDetails],recipeList) ]
    
    clusterDetails['VMids'] = VMIdList
    # hardcoded for now will pull later after getting details      
    clusterDetails['user'] = "penguinRaider" 
    # not sure if this is to be implemented or the user so putting both for now
    clusterDetails['userId'] = [i.owner_id for i in conn.get_all_instances() if i.id in reserveId ]
    clusterDetails['stack'] = "hadoop"       # as per blueprint
    clusterDetails['created_at'] = [i[1] for i in allVMDetails]
    clusterDetails['updated_at'] = "NA"
    clusterDetails['status'] = [i[2] for i in allVMDetails]
    print clusterDetails

    return clusterDetails

