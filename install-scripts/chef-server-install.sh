generate_password() {
    cd /tmp
    rand1=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1`
    rand2=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1`
    echo $rand1$rand2 > $1
}

download_install_chef() {
	wget https://opscode-omnibus-packages.s3.amazonaws.com/ubuntu/12.04/x86_64/chef_11.6.0-1.ubuntu.12.04_amd64.deb -O /tmp/chef-client.deb
	wget https://opscode-omnibus-packages.s3.amazonaws.com/ubuntu/12.04/x86_64/chef-server_11.0.8-1.ubuntu.12.04_amd64.deb -O /tmp/chef-server.deb
	sudo dpkg -i /tmp/chef-server.deb /tmp/chef-client.deb
}

configure_chef_server() {

	chef_server_ip=`ifconfig eth0 | grep -i 'inet '| cut -d ':' -f 2 | cut -d ' ' -f 1`

	if [ -n http_proxy ] || [ -n HTTP_PROXY ]
		then
		export no_proxy=localhost,127.0.0.1
	fi

	chef-server-ctl reconfigure
}

configure_knife() {

	mkdir $HOME/.chef
	touch $HOME/.chef/knife.rb

	knife configure -u $USER \
	--validation-client-name chef-validator \
	--validation-key /etc/chef-server/chef-validator.pem \
	-s https://$chef_server_ip \
	--admin-client-name admin \
	--admin-client-key /etc/chef-server/admin.pem \
	-c $HOME/.chef/knife.rb \
	-y -r ''

	knife user create \
	-a \
	-s https://localhost \
	-c $HOME/.chef/knife.rb \
	-u admin \
	-p generate_password \
	--disable-editing \
	-k /etc/chef-server/admin.pem \
	$USER > $HOME/.chef/$USER.pem

}

upload_cookbooks() {
	sudo apt-get -y install git
	mkdir /tmp/cookbooks

	git clone https://github.com/siel-iiith/hadoop-cookbook.git /tmp/cookbooks/hadoop
	git clone https://github.com/siel-iiith/hadoopstack-hadoop-cookbook.git /tmp/cookbooks/hadoopstack
	knife cookbook upload -o /tmp/cookbooks -a
}

download_install_chef
configure_chef_server
configure_knife
upload_cookbooks