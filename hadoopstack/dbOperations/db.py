

def getVMid(conn):
	allReservations=conn.get_all_instances()
	allInstances=[(str(i),str(i.launch_time),str(i.state)) for r in allReservations for i in r.instances]
	return allInstances
