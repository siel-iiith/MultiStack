Hadoop-Scripts
==============

Few hack scripts related to hadoop

1) hadoop_install.sh installs and configures hadoop on a cluster. The idea is to create a hadoop cluster hassle-free.

Syntax: ./hadoop_install Cluster_properties

2) ssh-id-copy.sh script is used to copy the ssh id of jobtracker to all slave machines. The intention is to provide passwordless access to all slave machines from the jobtracker.

Syntax: ./ssh-id-copy location_of_identity_file location_of_properties_file

3) add-node.sh adds a node to already running hadoop cluster.

Syntax: ./add-node.sh Node_ip