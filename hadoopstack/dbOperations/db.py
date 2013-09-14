import os

def getVMid(conn,currentReservationId=None):
    allReservations=conn.get_all_instances()
    
    allInstances=[(str(i.id),str(i.launch_time),str(i.state),str(r.id)) for 
                   r in allReservations if r.id in currentReservationId 
                   for i in r.instances]
    return allInstances
