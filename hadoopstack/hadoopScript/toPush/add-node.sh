#!/bin/bash
# adds a node in a running hadoop cluster
# Run this script on Master
# takes first argument as the ip_address/name of the node to be added

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 [options] Node_IP" >&2
  exit 1
fi

DFS_ONLY=0
MAPREDUCE_ONLY=0
INSTALL_DIR=/usr/local

while getopts "md" opt; do
   case $opt in

   m ) 	MAPREDUCE_ONLY=1
   		;;
   d ) 	DFS_ONLY=1;;
   \?)  echo "Invalid Option: $OPTARG"
   		usage
   		exit 1
   		;;
   esac
done

# Node reachable ?
echo "Checking connectivity to the node..."
ping $1 -c 5

if [ "$?" -ne 0 ]; then
  echo "Ping to the node $1 Failed. Check the node connectivity and try again" >&2
  exit 1
fi

#cd /usr/local/hadoop/conf
#echo $1 >> slaves

# copy hadoop
rsync -vaz --exclude='logs/*' /usr/local/hadoop $1:/usr/local/

#refresh nodelist
if [ $MAPREDUCE_ONLY -eq 0 ] ;then
	$INSTALL_DIR/hadoop/bin/hadoop mradmin -refreshNodes
	ssh $1 "$INSTALL_DIR/hadoop/bin/hadoop-daemon.sh start tasktracker"
fi

if [ $MAPREDUCE_ONLY -eq 0 ] ;then
	$INSTALL_DIR/hadoop/bin/hadoop dfsadmin -refreshNodes
	ssh $1 "$INSTALL_DIR/hadoop/bin/hadoop-daemon.sh start datanode"
fi

# verify
ssh $1 "jps"
