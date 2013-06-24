from fabric.api import *
import fabric
from hadoopstack.services import fabricConfig
import time

def update(localRepo,remoteRepo,privateKey): 
    while(True):
        try:

            run('ps aux')
            run('uptime')
            run("hostname")
            local("pwd")
            run('mkdir -p {0}'.format(remoteRepo))
            put(localRepo,remoteRepo)
            run('chmod 755 -R {0}'.format(remoteRepo))
            with cd('{0}/toTransfer'.format(remoteRepo)):
                run('source ~/.bashrc')
                run('ls -al ')
                
                run('./main.sh {1} {2}'.format(remoteRepo,privateKey,"properties"))
            break
        except fabric.exceptions.NetworkError:
            time.sleep(1)
            continue

def connectMaster(masterIp,keypair_name):   
    fileCompletePath="./hadoopstack/services/toTransfer/"+keypair_name+".pem"
    privateKey=keypair_name+".pem"
    env.key_filename = fileCompletePath
    env.host_string = masterIp
    env.user=fabricConfig.user
    env.reject_unknown_hosts=False
    #env.password = fabricConfig.Password
    env.disable_known_hosts=True
    localRepo="./hadoopstack/services/toTransfer"
    remoteRepo="./hadoopStackScripts"
    update(localRepo,remoteRepo,privateKey)



