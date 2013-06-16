import simplejson
import os

def jobDict(data):

    jobDetails={}

    jobDetails['name'] = data['jobs']['name']
    
    # Hardcoded, as we havnt made the user based form to submit a job
    jobDetails['user'] = "Stark"
    jobDetails['description'] = "Game of Thrones"
    jobDetails['assigned_to_cluster'] = "NA"
    jobDetails['submission_time'] = data['jobs']['deadline']
    jobDetails['start_time'] = "12"
    jobDetails['end_time'] = "7"
    jobDetails['estimated_duration'] = "5"
    jobDetails['current_status'] = "running"

    return jobDetails

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

    return clusterDetails

