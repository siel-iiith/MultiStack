import os

def getVMid(conn,currentReservationId="Nil"):
#	proxy=os.environ.get('http_proxy')
	foo=open("foo.txt","a+")
#foo.write("enve variable should be here in db dammit"+proxy+"\n")
	foo.flush()
#	del os.environ['http_proxy']

	allReservations=conn.get_all_instances()
	allInstances=[(str(i),str(i.launch_time),str(i.state)) for r in allReservations if r.id==currentReservationId for i in r.instances]
#	os.environ['http_proxy']=proxy

	return allInstances
