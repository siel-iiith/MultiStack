!/bin/bash

tar -xvf hadoop-2.0*
mkdir $HOME/yarn
mv hadoop-*.tar.gz myTar.tar.gz
mv hadoop-2.0* yarn/hadoop
sudo mkdir /tmp
sudo rm -r /tmp
sudo chmod a+rwx /tmp

export JAVA_HOME=/usr/lib/jvm/java-1.6.0-openjdk-amd64
export HADOOP_HOME=$HOME/yarn/hadoop
export HADOOP_MAPRED_HOME=$HOME/yarn/hadoop
export HADOOP_COMMON_HOME=$HOME/yarn/hadoop
export HADOOP_HDFS_HOME=$HOME/yarn/hadoop
export YARN_HOME=$HOME/yarn/hadoop
export HADOOP_CONF_DIR=$HOME/yarn/hadoop/etc/hadoop

mkdir -p $HOME/yarn/yarn_data/hdfs/namenode
mkdir -p $HOME/yarn/yarn_data/hdfs/datanode
#mkdir -p $HOME/yarn/tmp

cd $YARN_HOME/etc/hadoop/

# yarn-site.xml
#echo -e "<?xml version=\"1.0\"?>
echo "<configuration>
<property>
   <name>yarn.nodemanager.aux-services</name>
   <value>mapreduce.shuffle</value>
</property>
<property>
   <name>yarn.nodemanager.aux-services.mapreduce.shuffle.class</name>
   <value>org.apache.hadoop.mapred.ShuffleHandler</value>
</property>
</configuration>" > yarn-site.xml 

# core-site.xml
#echo -e "<?xml version=\"1.0\"?>
echo "<configuration>
<property>
   <name>fs.default.name</name>
   <value>hdfs://localhost:9000</value>
</property>
</configuration>" > core-site.xml

# hdfs-site.xml
#echo -e "<?xml version=\"1.0\"?>
echo "<configuration>
 <property>
   <name>dfs.replication</name>
   <value>1</value>
 </property>
<property>
   <name>dfs.namenode.name.dir</name>
   <value>file:/home/dharmesh/yarn/yarn_data/hdfs/namenode</value>
 </property>
 <property>
   <name>dfs.datanode.data.dir</name>
   <value>file:/home/dharmesh/yarn/yarn_data/hdfs/datanode</value>
 </property>
</configuration>" > hdfs-site.xml

# mapred-site.xml
#echo -e "<?xml version=\"1.0\"?>
echo "<configuration>
   <property>
      <name>mapreduce.framework.name</name>
      <value>yarn</value>
   </property>
</configuration>" > mapred-site.xml


cd $YARN_HOME
bin/hadoop namenode -format

sbin/hadoop-daemon.sh start namenode

jps

sbin/hadoop-daemon.sh start datanode

jps

sbin/yarn-daemon.sh start resourcemanager

jps

sbin/yarn-daemon.sh start nodemanager

jps

sbin/mr-jobhistory-daemon.sh start historyserver

jps
