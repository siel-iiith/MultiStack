from fabric.api import *
import fabric
from hadoopstack.services import fabricConfig
#from hadoopstack.services.prepareProperties import preparePropertyFile
import time

def update(): 
     while(True):
	   try:
	      run('ps aux')
              run('uptime')
	      run("hostname")
	      break
	        
	   except fabric.exceptions.NetworkError:
	       time.sleep(1)
	       continue

    #local(' rm -rf ~/.ssh/known_hosts ')
    #local('ssh-keygen -f "/home/hellboy2k8/.ssh/known_hosts" -R 10.2.4.81') #small Hack will find better way found better way see disable_known_hosts
    #run('ls -al')
  





def connectMaster(masterIp,conn):
	env.host_string = masterIp
	env.user=fabricConfig.user
	env.password = fabricConfig.Password
	env.disable_known_hosts=True
	
	update()



