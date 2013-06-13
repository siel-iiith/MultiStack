#!/bin/bash
# Downloads and configures hadoop on cluster.
# To Do
# Install Dependdencies like java, ssh etc
#
# Takes argument as properties file which gives the cluster parameters
# (see the example Properties file at https://github.com/dharmeshkakadia/Hadoop-Scripts/blob/master/properties)

# change JAVA_HOME according to your environment
JAVA_HOME=/usr/lib/jvm/java-1.6.0-openjdk-amd64

# Download URL
# URL=http://apache.techartifact.com/mirror/hadoop/common/hadoop-1.1.0/hadoop-1.1.0-bin.tar.gz

function usage () {
   cat <<EOF
Usage: $0 [options] Cluster_properties_file
	-u[URL]	download hadoop
	-j[Path_to_java]	use Java_Dir
	-p[install_dir]		Install hadoop at install_dir
	-r[proxyhost:proxy-port]	use proxy with wget
	-o			Do not format the namenode
	-d 			DFS data Directory
	-v			executes and prints out verbose messages
   	-h  		displays this help
EOF
}


# Argument check
if [ $# -lt 1 ]
then
        usage;
        exit 1
else
        if [ ! -f $1 ]
        then
                echo "$1 File does not exist"
        else
                PROPERTIES_FILE=$1
                shift
                echo "Using Properties file : $PROPERTIES_FILE"
        fi
fi

# Hadoop Installation localation
INSTALL_DIR=/usr/local
PROXY=
HADOOP_TEMP=/app/hadoop/tmp
DFS_DATA_DIR=/media/disk3
HDFS_URI=hdfs://`grep -i namenode $PROPERTIES_FILE | cut -f 2`
JOBTRACKER_URI=`grep -i jobtracker $PROPERTIES_FILE | cut -f 2`
DFS_REPLICATION=2
NN_FORMAT=1
NAMENODE=`grep -i namenode $PROPERTIES_FILE  | tr -s ' ' | cut -f 2 -d' '| cut -d ":" -f 1`
DATANODE=`grep -i datanode $PROPERTIES_FILE  tr -s ' ' | cut -f 2 -d' '`
JOBTRACKER=`grep -i jobtracker $PROPERTIES_FILE  | tr -s ' ' | cut -f 2 -d' '| cut -d ":" -f 1`
TASKTRACKER=`grep -i tasktracker $PROPERTIES_FILE  tr -s ' ' | cut -f 2 -d' '`

while getopts "r:u:j:p:d:vhmf" opt; do
   case $opt in

   r )	PROXY=$OPTARG
		echo "Using PROXY=$PROXY"
		;;
   u )  echo "Downloading hadoop tar from $OPTARG"
	   	wget -e "http_proxy=$PROXY" $OPTARG
		;;
   j ) 	JAVA_HOME=$OPTARG
   		;;
   p ) 	INSTALL_DIR=$OPTARG
   		;;
   d ) 	DFS_DATA_DIR=$OPTARG
   		;;
   o ) 	NN_FORMAT=0;;
   v )	VERBOSE=1;;
   h )  usage ;;
   \?)  echo "Invalid Option: $OPTARG"
   		usage
   		exit 1
   		;;
   :)   echo "Option -$OPTARG requires an argument." >&2
        exit 1
        ;;
   esac
done

echo "Using JAVA_HOME=$JAVA_HOME"

if [ ! -d "$JAVA_HOME" ];
then
	echo "JAVA_HOME is pointing to $JAVA_HOME, which doesn't exist. Use -j option to specify the correct JAVA_HOME location"
	exit
fi

export JAVA_HOME=$JAVA_HOME
HADOOP_DIR=$INSTALL_DIR/hadoop

# Move hadoop
hadoop_tar=`find -name hadoop*.tar.gz`

if [ ! -f "$hadoop_tar" ];
then
	echo "Hadoop tar not found at location : $hadoop_tar. You can download form hadoop mirror using -u option"
	exit
fi


# configure /app/hadoop/tmp $2 $JAVA_HOME
function configure(){
	echo "-----------starting configuration-------------"
	sudo rm -rf $HADOOP_TEMP
	sudo mkdir -p $HADOOP_TEMP

	cd $HADOOP_DIR/conf/
	# actually not needed, used by start-all.sh and stop-all.sh
	# master and slave files
	echo $NAMENODE > masters
	echo "$DATANODE" > slaves
	echo "$TASKTRACKER" >> slaves
	#run uniq on slaves

	echo "export JAVA_HOME=$JAVA_HOME" >> hadoop-env.sh

    if [ -n $NAMENODE ] ;then #core-site.xml
	echo -e "<?xml version=\"1.0\"?><?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?><configuration><property><name>hadoop.tmp.dir</name><value>$HADOOP_TEMP</value><description>A base for other temporary directories.</description></property><property><name>fs.default.name</name><value>$HDFS_URI</value><description>The name of the default file system.  A URI whosescheme and authority determine the FileSystem implementation.  Theuri's scheme determines the config property (fs.SCHEME.impl) namingthe FileSystem implementation class.  The uri's authority is used todetermine the host, port, etc. for a filesystem.</description></property></configuration>" > core-site.xml

    # hdfs-site.xml
	echo -e "<?xml version=\"1.0\"?><?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?><configuration><property><name>dfs.replication</name><value>$DFS_REPLICATION</value><description>Default block replication.The actual number of replications can be specified when the file is created.The default is used if replication is not specified in create time.</description></property><property><name>dfs.data.dir</name><value>$DFS_DATA_DIR</value><description>Determines where on the local filesystem an DFS data node should store its blocks. If this is a comma-delimited list of directories, then data will be stored in all named directories, typically on different devices. Directories that do not exist are ignored.</description></property></configuration>" > hdfs-site.xml
    fi

    if [ -n $JOBTRACKER ] ; then	#mapred-site.xml
	echo -e "<?xml version=\"1.0\"?><?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?><configuration><property><name>mapred.job.tracker</name><value>$JOBTRACKER_URI</value><description>The host and port that the MapReduce job tracker runs </description></property></configuration>" > mapred-site.xml

    fi
}


# rsync to slaves $(cat /usr/local/hadoop/conf/slaves)
function copyToSlaves(){
	for srv in $1 ; do
	  echo "Copying to $srv...";
	  rsync -avz --exclude='logs/*' $HADOOP_DIR/ $srv:$HADOOP_DIR/
	  ssh $srv "rm -fR /app"
	done
}

function startDaemon(){
	for srv in $1 ; do
	  echo "Starting $2 on $srv...";
	  ssh $srv "$HADOOP_DIR/bin/hadoop-daemon.sh start $2"
	done
}

# Verify the status of hadoop-daemons
function verifyJPS(){
	echo "-----------Verfing hadoop daemons-------------"
	# verify
	for srv in $1; do
	  echo "Running jps on $srv.........";
	#  ssh $srv "ps aux | grep -v grep | grep java"
	  ssh $srv "jps"
	done
}

sudo rm -rf $HADOOP_DIR
tar xzf $hadoop_tar -C $INSTALL_DIR
sudo mv $INSTALL_DIR/hadoop-* $HADOOP_DIR

configure $HADOOP_TEMP $2 $JAVA_HOME

copyToSlaves "$DATANODE"
copyToSlaves $NAMENODE
copyToSlaves "$TASKTRACKER"
copyToSlaves $JOBTRACKER

echo "-----------starting hadoop cluster-------------"
# format namenode
#cd $HADOOP_DIR/bin/

if [ $NN_FORMAT -eq 1 ] ;then
	echo "Formatting the NameNode........"
	ssh $NAMENODE "$HADOOP_DIR/bin/hadoop namenode -format"
fi

startDaemon "$NAMENODE" "namenode"
startDaemon "$DATANODE" "datanode"
startDaemon "$JOBTRACKER" "jobtracker"
startDaemon "$TASKTRACKER" "tasktracker"

verifyJPS $NAMENODE
verifyJPS "$DATANODE"
verifyJPS $JOBTRACKER
verifyJPS "$TASKTRACKER"

echo "done"
