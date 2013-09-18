chef_server_ip=`ifconfig eth0 | grep -i 'inet '| cut -d ':' -f 2 | cut -d ' ' -f 1`

wget https://opscode-omnibus-packages.s3.amazonaws.com/ubuntu/12.04/x86_64/chef_11.6.0-1.ubuntu.12.04_amd64.deb -O /tmp/chef-client.deb
wget https://opscode-omnibus-packages.s3.amazonaws.com/ubuntu/12.04/x86_64/chef-server_11.0.8-1.ubuntu.12.04_amd64.deb -O /tmp/chef-server.deb

sudo dpkg -i /tmp/chef-server.deb /tmp/chef-client.deb

chef-server-ctl reconfigure

knife configure -u ubuntu --validation-client-name chef-validator --validation-key /etc/chef-server/chef-validator.pem -s https://$chef_server_ip --admin-client-name admin --admin-client-key /etc/chef-server/admin.pem -c /home/ubuntu/.chef/knife.rb -y -r ''
knife user create -a -s https://localhost -c /home/ubuntu/.chef/knife.rb -u admin -p $RANDOM --disable-editing -k /etc/chef-server/admin.pem ubuntu > /home/ubuntu/.chef/ubuntu.pem

sudo apt-get -y install git
mkdir /tmp/cookbooks

git clone https://github.com/siel-iiith/hadoop-cookbook.git /tmp/cookbooks/hadoop
git clone https://github.com/siel-iiith/hadoopstack-hadoop-cookbook.git /tmp/cookbooks/hadoopstack
knife cookbook upload -o /tmp/cookbooks hadoop
