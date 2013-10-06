from fabric.api import env
from fabric.api import run
from fabric.api import sudo

class Remote:
    """
    A class to handle ssh communications with remote systems.
    """

    def __init__(self, address, user, key_location):
        """
        Remote class initialization function.

        @param  address: IP address or the remote host
        @type   address: C{str}

        @param  user: Username to be used for authentication
        @type   user: C{str}

        @param  key_location: Path of the private key_location
        @type   key_location: C{str}
        """

        self.address = address
        self.user = user
        self.key = key_location
        self.env = env

    def run(self, command):
        """
        Execute a command on the remote host as self.user

        @param  command: Command to be executed
        @type   command: C{str}
        """
        env.host_string = self.address
        env.key_filename = self.key
        env.user = self.user
        env.disable_known_hosts=True

        return  run(command)

    def sudo(self, command, user=None):
        """
        Executes command on the remote host using sudo as user

        @param  command: Command to be executed
        @type   command: C{str}

        @param  user: User on whose behalf the command will be executed
        @type   user: C{str}
        """

        return sudo(command, user=user)
