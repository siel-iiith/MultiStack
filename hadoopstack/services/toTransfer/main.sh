#!/bin/bash

# $1 is identity file(.pem)
# $2 is properties file

#script_hadoop_install="https://raw.github.com/dharmeshkakadia/Hadoop-Scripts/master/hadoop_install.sh"
#ssh_copy_id="https://github.com/shredder12/Hadoop-Scripts/raw/master/ssh-id-copy.sh"
script_hadoop_install="hadoop_install.sh"
ssh_copy_id="ssh-id-copy.sh"



#hadoop_download="http://apache.techartifact.com/mirror/hadoop/common/hadoop-1.1.0/hadoop-1.1.0-bin.tar.gz"
hadoop_download="http://archive.apache.org/dist/hadoop/core/hadoop-1.1.0/hadoop-1.1.0-bin.tar.gz"
chmod 0600 $1
pwd
echo "sasadasd"

whoami
echo "sadsjsajdjhasjdhsaj"
env | grep proxy
echo "yada yada "
#ping www.google.com
#wget $hadoop_download
#exit 
#wget $script_hadoop_install -O hadoop_install.sh
chmod a+x hadoop_install.sh

#wget $ssh_copy_id -O ssh-copy-id.sh
chmod a+x ssh-copy-id.sh
echo "going to ssh copyid"
./ssh-copy-id.sh $1 $2
echo "coming from copy id"
./hadoop_install.sh $2

