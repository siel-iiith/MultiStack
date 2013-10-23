"""
Provides Class for OpenStack provider
"""

from time import sleep

from flask import current_app
from novaclient.v1_1 import Client as novaclient

from multistack.providers.base import BaseProvider
from multistack.constants import *

class OpenStackProvider(BaseProvider):
    """
    Implements OpenStack Provider
    """

    def _connect(self, credentials):
        return novaclient(
                    credentials['username'],
                    credentials['password'],
                    credentials['tenant'],
                    credentials['auth_url']
                    )

    def _get_server_obj(self, instance_id):
        """Returns server object with id, instance_id"""

        for server in self.conn.servers.list():
            if server.id == instance_id:
                return server

    def _get_flavor_id(self, flavor_name):
        for flavor in self.conn.flavors.list():
            if flavor.name == flavor_name:
                return flavor.id

    def _get_flavor_name(self, flavor_id):
        for flavor in self.conn.flavors.list():
            if flavor.id == flavor_id:
                return flavor.name

    def _get_image_id(self, image_name):
        for image in self.conn.images.list():
            if image.name == image_name:
                return image.id

    def _get_public_ip(self, instance_id):
        for server in self.conn.servers.list():
            if len(server.addresses['private']) == 1:
                return None
            else:
                return str(server.addresses['private'][1]['addr'])

    def _save_private_key(self, key, location):
        fd = open(location, 'w+')
        fd.write(key)
        fd.close()

    def is_instance_running(self, instance_id):
        count = 0
        while True:
            server = self.conn.servers.get(instance_id)
            if server.id == instance_id:
                if server.__dict__['OS-EXT-STS:power_state'] == 1:
                    return True
                else:
                    sleep(2)
                    count += 2
                    if count >= INSTANCE_TIMEOUT:
                        return False

    def get_all_addresses(self):
        """Returns a list of public addresses"""

        addresses = list()
        for addr in self.conn.floating_ips.list():
            addresses.append(str(addr.ip))

        return addresses

    def associate_public_ip(self, instance_id):
        """Associates public_ip with the instance"""

        addr = self.conn.floating_ips.create()
        print addr.ip
        server = self._get_server_obj(instance_id)
        print server
        server.add_floating_ip(addr)
        current_app.logger.info("IP Associated: {0}".format(addr.ip))

    def release_public_ip(self, public_ip):
        """
        Releases public_ips attached to the instances

        @param public_ip: public_ip
        @type public_ip: C{str}
        """
        if public_ip == ('' or None):
            return

        for addr in self.conn.floating_ips.list():
            if addr.instance_id is None:
                addr.delete()
            else:
                server = self._get_server_obj(addr.instance_id)
                server.remove_floating_ip(addr.ip)
                addr.delete()

    def boot_instances(self, 
                    name,
                    number, 
                    keypair,
                    security_groups,
                    flavor,
                    image_id
                    ):
        """
        Boot Instances

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

        @type image_id: image-id
        @type image_id: string
        """

        servers = list()
        instances = list()
        server = dict()

        for count in range(0, number):
            instance = self.conn.servers.create(
                                            name = name,
                                            image = self._get_image_id(image_id),
                                            min_count = 1, 
                                            max_count = 1,
                                            key_name = keypair,
                                            security_groups = security_groups,
                                            flavor = self._get_flavor_id(flavor)
                                            )

            if self.is_instance_running(instance.id):
                self.associate_public_ip(instance.id)
                instances.append(instance)

        for instance in instances:
            instance = self.conn.servers.get(instance.id)
            server['id'] = instance.id
            server['private_ip_address'] = str(instance.addresses['private'][0]['addr'])
            server['ip_address'] = str(instance.addresses['private'][1]['addr'])
            server['flavor'] = self._get_flavor_name(instance.flavor)
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

        keypair = self.conn.keypairs.create(keypair_name)
        self._save_private_key(keypair.private_key, '/tmp/{0}.pem'.format(keypair_name))

        # TODO - Save this keypair file in the mongodb

    def create_security_groups(self, sec_master_name, sec_slave_name):
        """
        Creates Security groups.

        @param sec_master_name: Name of master's security group
        @type sec_master_name: string

        @param sec_slave_name: Name of slave's security group
        @type sec_slave_name: string
        """

        sec_slave = self.conn.security_groups.create(
                                    sec_slave_name,
                                    "Security group for the slaves"
                                    )
        sec_master = self.conn.security_groups.create(
                                    sec_master_name,
                                    "Security group for the master"
                                    )

        self.conn.security_group_rules.create(
                                sec_master.id,
                                ip_protocol = 'tcp',
                                from_port = '1',
                                to_port = '65535'
                                )
        self.conn.security_group_rules.create(
                                sec_master.id,
                                ip_protocol = 'udp',
                                from_port = '1',
                                to_port = '65535'
                                )
        self.conn.security_group_rules.create(
                                sec_master.id,
                                ip_protocol = 'icmp',
                                from_port = '-1',
                                to_port = '-1'
                                )

        self.conn.security_group_rules.create(
                                sec_slave.id,
                                ip_protocol = 'tcp',
                                from_port = '1',
                                to_port = '65535'
                                )
        self.conn.security_group_rules.create(
                                sec_slave.id,
                                ip_protocol = 'udp',
                                from_port = '1',
                                to_port = '65535'
                                )
        self.conn.security_group_rules.create(
                                sec_slave.id,
                                ip_protocol = 'icmp',
                                from_port = '-1',
                                to_port = '-1'
                                )

    def delete_keypair(self, keypair_name):
        """Deletes Keypair"""
        
        keypair = self.conn.keypairs.get(keypair_name)
        keypair.delete()

    def delete_security_groups(self, security_groups):
        """
        Delete security groups

        @param security_groups: List of security groups to be deleted
        @type security_groups: List
        """

        for sg in self.conn.security_groups.list():
            if sg.name in security_groups:
                sg.delete()

    def terminate_instances(self, instance_ids):
        """
        Terminate Instances

        @param instance_ids: List of Instance IDs to be deleted
        @type instance_ids: List
        """

        if len(instance_ids) == 0:
            return

        flag = True
        while flag:
            flag = False
            for server in self.conn.servers.list():
                if server.id in instance_ids:
                    flag = True
                    addr = self._get_public_ip(server.id)
                    self.release_public_ip(addr)
                    server.delete()
                    instance_ids.remove(server.id)
            sleep(2)
