#!/bin/bash

# $1 is identity file(.pem)
# $2 is properties file

script_hadoop_install="https://raw.github.com/dharmeshkakadia/Hadoop-Scripts/master/hadoop_install.sh"
ssh_copy_id="https://github.com/shredder12/Hadoop-Scripts/raw/master/ssh-id-copy.sh"
hadoop_download="http://apache.techartifact.com/mirror/hadoop/common/hadoop-1.1.0/hadoop-1.1.0-bin.tar.gz"

chmod 0600 $1

wget $hadoop_download

wget $script_hadoop_install -O hadoop_install.sh
chmod a+x hadoop_install.sh

wget $ssh_copy_id -O ssh-copy-id.sh
chmod a+x ssh-copy-id.sh

./ssh-copy-id.sh $1 $2

./hadoop_install.sh $2

