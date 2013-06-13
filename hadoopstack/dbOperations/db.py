import os

def getVMid(conn,currentReservationId="Nil"):
    #foo=open("foo.txt","a+")
    #foo.write("entering the getvmfile")
    #foo.write(str(currentReservationId))
    #foo.flush()
    allReservations=conn.get_all_instances()
    
    allInstances=[(str(i),str(i.launch_time),str(i.state),str(r.id)) for 
                   r in allReservations if r.id in currentReservationId 
                   for i in r.instances]
    return allInstances
