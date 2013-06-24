#!/bin/bash
# Downloads and configures hadoop on cluster.
# To Do
# Install Dependdencies like java, ssh etc
#
# Takes argument as properties file which gives the cluster parameters
# (see the example Properties file at https://github.com/dharmeshkakadia/Hadoop-Scripts/blob/master/properties)

# change JAVA_HOME according to your environment
JAVA_HOME=/usr/lib/jvm/java-1.6.0-openjdk-amd64
#JAVA_HOME=/usr/lib/jvm/java-7-oracle


# Download URL
# URL=http://apache.techartifact.com/mirror/hadoop/common/hadoop-1.1.0/hadoop-1.1.0-bin.tar.gz
echo "sadajhdjsahdjasdjahsjhdasjhasjhjashjsahjsahlaskasjklasjlasjksa sadsabdjshajhasas dasnbdjsajdabs assajbdjsahdjsahdsjahahdjaslsajlsahsalhasl"



#additions 
#adding pem file to be used while ssh $1
#changed cut command to cut according to properties







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

echo $2
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

echo "the properties files is "
echo $PROPERTIES_FILE
echo "the properties file ends"

echo "came here"
# Hadoop Installation localation
#PEM_FILE="AS"
USER="ubuntu"
PRESENT_DIRECTORY=`pwd`

echo "pem file starts"
echo $PEM_FILE
echo "pem file ends"
INSTALL_DIR=/usr/local
PROXY=
echo "came here too"
HADOOP_TEMP=/app/hadoop/tmp
echo "came here too 1"

DFS_DATA_DIR=/media/disk3
echo "came here too 2"
echo $PROPERTIES_FILE
echo "end here\n"
HDFS_URI=hdfs://`grep -i namenode $PROPERTIES_FILE | tr -s ' '| cut -f 2 -d' '`

echo $HDFS_URI
echo "came here too 3"
echo "\n"
JOBTRACKER_URI=`grep -i jobtracker $PROPERTIES_FILE | tr -s ' ' | cut -f 2 -d' '`
DFS_REPLICATION=2
NN_FORMAT=1
echo "came here too too"
NAMENODE=`grep -i namenode $PROPERTIES_FILE  | tr -s ' '| cut -f 2 -d' '| cut -d ":" -f 1`
DATANODE=`grep -i datanode $PROPERTIES_FILE  | tr -s ' '| cut -f 2 -d' '`
JOBTRACKER=`grep -i jobtracker $PROPERTIES_FILE  | tr -s ' ' | cut -f 2 -d' '| cut -d ":" -f 1`
TASKTRACKER=`grep -i tasktracker $PROPERTIES_FILE  | tr -s ' '| cut -f 2 -d' '`

echo "here there "
#echo NAMENODE,JOBTRACKER,DATANODE,NAMENODE,HDFS_URI,JOBTRACKER_URI;
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
    pwd
    ls -al
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
	pwd
	echo "started here"
	echo $NAMENODE | sudo tee masters
	echo "$DATANODE" | sudo tee slaves
	echo "$TASKTRACKER" | sudo tee -a slaves
	#run uniq on slaves
	echo "done here "
	pwd
	echo "export JAVA_HOME=$JAVA_HOME" | sudo tee -a hadoop-env.sh

    if [ -n $NAMENODE ] ;then #core-site.xml
	echo -e "<?xml version=\"1.0\"?><?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?><configuration><property><name>hadoop.tmp.dir</name><value>$HADOOP_TEMP</value><description>A base for other temporary directories.</description></property><property><name>fs.default.name</name><value>$HDFS_URI</value><description>The name of the default file system.  A URI whosescheme and authority determine the FileSystem implementation.  Theuri's scheme determines the config property (fs.SCHEME.impl) namingthe FileSystem implementation class.  The uri's authority is used todetermine the host, port, etc. for a filesystem.</description></property></configuration>" | sudo tee  core-site.xml

    # hdfs-site.xml
	echo -e "<?xml version=\"1.0\"?><?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?><configuration><property><name>dfs.replication</name><value>$DFS_REPLICATION</value><description>Default block replication.The actual number of replications can be specified when the file is created.The default is used if replication is not specified in create time.</description></property><property><name>dfs.data.dir</name><value>$DFS_DATA_DIR</value><description>Determines where on the local filesystem an DFS data node should store its blocks. If this is a comma-delimited list of directories, then data will be stored in all named directories, typically on different devices. Directories that do not exist are ignored.</description></property></configuration>" | sudo tee hdfs-site.xml
    fi

    if [ -n $JOBTRACKER ] ; then	#mapred-site.xml
	echo -e "<?xml version=\"1.0\"?><?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?><configuration><property><name>mapred.job.tracker</name><value>$JOBTRACKER_URI</value><description>The host and port that the MapReduce job tracker runs </description></property></configuration>" | sudo tee mapred-site.xml

    fi
}


# rsync to slaves $(cat /usr/local/hadoop/conf/slaves)
function copyToSlaves(){
	echo "the file is is is is is "
	echo $PEM_FILE
	echo $HADOOP_DIR
	pwd
	echo "the file ends"
	for srv in $1 ; do
	  echo "Copying to $srv...";
	  echo "Sadsadsadsadsadsadsadsadashdsajhsjdahjdsahjsdahjsahjdshajsahjhasjhsajhdsajhsajhd"	
	  echo $HADOOP_DIR
	  echo $srv
	  rsync -avz --exclude='logs/*'  --rsync-path="sudo rsync" $HADOOP_DIR/ $srv:$HADOOP_DIR/

	  echo "reached here too too yada yada yada"
	  #CUR_DIR=`pwd`
	  

	  #ssh  -i $PRESENT_DIRECTORY/$PEM_FILE -o StrictHostKeyChecking=no   $USER@$srv "rm -fR /app"
	  echo "this is done"
	  ssh $srv "sudo rm -fR /app"
	  echo "got off here "
	done
}

function startDaemon(){
	for srv in $1 ; do
	  echo "Starting $2 on $srv...";
	  #ssh -i $PRESENT_DIRECTORY/$PEM_FILE -o StrictHostKeyChecking=no    $USER@$srv "$HADOOP_DIR/bin/hadoop-daemon.sh start $2"
	  ssh $srv "sudo $HADOOP_DIR/bin/hadoop-daemon.sh start $2"
	  echo "got here "
	done
}

# Verify the status of hadoop-daemons
function verifyJPS(){
	echo "-----------Verfing hadoop daemons-------------"
	# verify
	for srv in $1; do
	  echo "Running jps on $srv.........";
	  #ssh $srv "ps aux | grep -v grep | grep java"
	  #ssh    -i $PRESENT_DIRECTORY/$PEM_FILE -o StrictHostKeyChecking=no  $USER@$srv "jps"
	  ssh  $srv "jps"

	done
}

sudo rm -rf $HADOOP_DIR
echo "Reached here \n"
sudo tar xzf $hadoop_tar -C $INSTALL_DIR


sudo mv $INSTALL_DIR/hadoop-* $HADOOP_DIR
echo "this is it"
echo $2 
echo "got off"
configure $HADOOP_TEMP $2 $JAVA_HOME

#copyToSlaves "$DATANODE"
#copyToSlaves $NAMENODE
copyToSlaves "$TASKTRACKER"
copyToSlaves $JOBTRACKER

echo "-----------starting hadoop cluster-------------"
# format namenode
#cd $HADOOP_DIR/bin/
echo "came here too"
if [ $NN_FORMAT -eq 1 ] ;then
	echo "Formatting the NameNode........"
	ssh $NAMENODE "$HADOOP_DIR/bin/hadoop namenode -format"
	echo "formatting of namenode done"
fi

echo "going here "
#startDaemon "$NAMENODE" "namenode"
#startDaemon "$DATANODE" "datanode"
startDaemon "$JOBTRACKER" "jobtracker"
startDaemon "$TASKTRACKER" "tasktracker"

#verifyJPS $NAMENODE
#verifyJPS "$DATANODE"
verifyJPS $JOBTRACKER
echo "going to jps code"
verifyJPS "$TASKTRACKER"

echo "done"
