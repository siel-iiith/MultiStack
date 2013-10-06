from fabric.api import env
from fabric.api import run

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

        env.host_string = address
        env.key_filename = key_location
        env.user = user
        env.disable_known_hosts=True

        self.env = env

    def execute(self, command):
        """
        Execute a command on the remote host

        @param  command: Command to be executed
        @type   command: C{str}
        """

        env = self.env
        return run(command)