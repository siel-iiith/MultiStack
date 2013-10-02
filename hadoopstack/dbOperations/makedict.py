import simplejson
import os
import datetime

def jobDict(data):

    jobDetails={}

    jobDetails['name'] = data['jobs']['name']
    
    # Hardcoded, as we havnt made the user based form to submit a job
    jobDetails['user'] = "Stark"
    jobDetails['description'] = "No Description"
    jobDetails['assigned_to_cluster'] = "NA"
    # When the job is submitted. Lets save epoch for the time being.
    jobDetails['submission_time'] = datetime.datetime.utcnow().isoformat()
    # When the job is started/scheduled
    jobDetails['start_time'] = "12"
    # When the jop has finished
    jobDetails['end_time'] = "7"
    # How much time left
    jobDetails['estimated_duration'] = "5"
    # Deadline to be met by user
    jobDetails['deadline'] = data['jobs']['deadline']
    # Running/Completed/Deleted/waiting/pending
    jobDetails['status'] = "pending"

    return jobDetails
