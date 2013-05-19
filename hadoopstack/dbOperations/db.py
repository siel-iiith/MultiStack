

def getVMid(conn):
	allReservations=conn.get_all_instances()
	allInstances=[(i,i.launch_time,i.state) for r in allReservations for i in r.instances]
	return allInstances
