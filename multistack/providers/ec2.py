from time import sleep

from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import EC2RegionInfo
from flask import current_app

from multistack.providers.base import BaseProvider


class EC2Provider(BaseProvider):
    """
    A provider class specific to support EC2 API.

    The features of this class will be inclined towards supporting
    AWS. Its preferable to support other cloud providers through a
    specific class.
    """

    def _connect(self, credentials):
        """
        A general function to connect cloud provider endpoing using EC2 API

        @param credentials: A dictionary containing ec2 specific parameters for
        connecting to the endpoint.
        @type credentials: dictionary

        @return A boto ec2 connection object
        """

        url = credentials['ec2_url']
        url_path = str()
        url_endpoint = url.split('/')[2]
        url_protocol = url.split('/')[0].split(':')[0]

        if url_protocol == "https":
            secure = True
        elif url_protocol == "http":
            secure = False

        if len(url.split(':')) > 2:
            url_port = url.split(':')[2].split('/')[0]
            url_path = url.split(url_port)[1]

        hs_region = EC2RegionInfo(name = credentials['ec2_region'], endpoint = url_endpoint)
        
        conn = EC2Connection(
                        aws_access_key_id = credentials['ec2_access_key'],
                        aws_secret_access_key = credentials['ec2_secret_key'],
                        is_secure = secure,
                        path = url_path,
                        region = hs_region
                        )
        return conn

    def associate_public_ip(self, instance_id):
        """Associates public_ip with the instance"""

        addr = self.conn.allocate_address()
        addr.associate(instance_id)
        current_app.logger.info("IP Associated: {0}".format(addr.public_ip))
        return addr.public_ip

    def release_public_ip(self, public_ip):
        """
        Releases public_ips attached to the instances

        @param public_ip: public_ip
        @type public_ip: C{str}
        """
        if public_ip == ('' or None):
            return

        for addr in self.conn.get_all_addresses(addresses = [public_ip]):
            if addr.instance_id is None:
                addr.release()
            else:
                addr.disassociate()
                addr.release()

    def boot_instances(
                    self,
                    name,
                    number,
                    keypair,
                    security_groups,
                    flavor,
                    image_id
                    ):
        """
        Boot Instances and Associate a Public IP with each

        @param name: Name of the instance
        @type name: string

        @param number: number of instances to boot
        @type number: int

        @param keypair: Keypair name
        @type keypair: string

        @param security_groups: name of the security groups
        @type security_groups: string

        @param flavor: instance type
        @type flavor: string

        @param image_id: image-id
        @type image_id: string
        """

        servers = list()
        server = dict()

        reservation = self.conn.run_instances(image_id, int(number), 
                                        int(number), keypair, security_groups,
                                        instance_type=flavor)
        
        for instance in reservation.instances:
            instance.add_tag('Name', name)
            while instance.state == 'pending':
                sleep(4)
                current_app.logger.info("waiting for instance status to update")
                instance.update()

        for instance in reservation.instances:
            self.associate_public_ip(instance.id)
            instance.update()
            server['id'] = instance.id
            server['private_ip_address'] = instance.private_ip_address
            server['ip_address'] = instance.ip_address
            server['flavor'] = instance.instance_type
            server['role'] = name.split('-')[-1]
            servers.append(server)

        return servers

    def create_keypair(self, keypair_name, key_dir = '/tmp'):
        """
        Creates keypair and saves it in key_dir directory

        @param keypair_name: Keypair name
        @type keypair_name: string

        @param key_dir: Destination folder of keypair
        @type key_dir: string
        """

        keypair = self.conn.create_key_pair(keypair_name)
        keypair.save(key_dir)

        # TODO - Save this keypair file in the mongodb

    def create_security_groups(self, sec_master_name, sec_slave_name):
        """
        Creates Security groups.

        @param sec_master_name: Name of master's security group
        @type sec_master_name: string

        @param sec_slave_name: Name of slave's security group
        @type sec_slave_name: string
        """

        sec_slave = self.conn.create_security_group(sec_slave_name,
                                            "Security group for the slaves")
        sec_master = self.conn.create_security_group(sec_master_name,
                                            "Security group for the master")

        # For now we'll authorize all the connections. We can add
        # granular rules later
        sec_slave.authorize(
            ip_protocol = "tcp",
            from_port = 1,
            to_port = 65535,
            cidr_ip = "0.0.0.0/0")

        sec_slave.authorize(
            ip_protocol = "udp",
            from_port = 1,
            to_port = 65535,
            cidr_ip = "0.0.0.0/0")

        sec_slave.authorize(
            ip_protocol = "icmp",
            from_port = -1,
            to_port = -1,
            cidr_ip = "0.0.0.0/0")  

        sec_master.authorize(
            ip_protocol = "tcp",
            from_port = 1,
            to_port = 65535,
            cidr_ip = "0.0.0.0/0")

        sec_master.authorize(
            ip_protocol = "udp",
            from_port = 1,
            to_port = 65535,
            cidr_ip = "0.0.0.0/0")    

        sec_master.authorize(
            ip_protocol = "icmp",
            from_port = -1,
            to_port = -1,
            cidr_ip = "0.0.0.0/0")

    def delete_keypair(self, keypair_name):
        """Delete a Keypair"""

        for keypair in self.conn.get_all_key_pairs(keynames = [keypair_name]):
            keypair.delete()

    def delete_security_groups(self, security_groups):
        """
        Delete security groups

        @param security_groups: List of security groups to be deleted
        @type security_groups: List
        """

        if len(security_groups) == 0:
            return

        flag = True
        print security_groups
        while flag:
            flag = False
            for sg in self.conn.get_all_security_groups(groupnames = security_groups):
                if len(sg.instances()) == 0:
                    try:
                        sg.delete()
                        security_groups.remove(sg.name)
                    except:
                        flag = True
                        continue
                else:
                    flag = True

    def terminate_instances(self, instance_ids):
        """
        Terminate Instances

        @param instance_ids: List of Instance IDs to be deleted
        @type instance_ids: List
        """

        if len(instance_ids) == 0:
            return

        print instance_ids

        flag = True
        while flag:
            flag = False
            for instance in self.conn.get_only_instances(instance_ids = instance_ids):
                if instance.state == 'running':
                    flag = True
                    instance.terminate()
                    self.release_public_ip(instance.ip_address)

                elif instance.state != 'terminated':
                    flag = True
