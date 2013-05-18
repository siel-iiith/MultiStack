######Installing mongoDB Daemon



#add GPG key
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
#add to the source list
echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/10gen.list
#update
sudo apt-get update
#install
sudo apt-get install mongodb-10gen


