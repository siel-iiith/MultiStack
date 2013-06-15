from fabric.api import *
import fabric
from hadoopstack.services import fabricConfig
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

def connectMaster(masterIp,conn):
    env.key_filename = "/home/hellboy2k8/.ssh/id_rsa"
    env.host_string = masterIp
    env.user=fabricConfig.user
    env.reject_unknown_hosts=False
    env.password = fabricConfig.Password
    env.disable_known_hosts=True
    update()



