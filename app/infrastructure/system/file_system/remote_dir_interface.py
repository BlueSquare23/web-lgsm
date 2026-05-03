import os

from app.infrastructure.system.ssh.client import SSHClientInterface

from app.utils.helpers import log_wrap
from .dir_interface import DirInterface

class SSHDirInterface(DirInterface):
    """Interface for SSH/SFTP dir operations"""

    def __init__(self, server, client_interface=SSHClientInterface()):
        super().__init__(server)
        self.client_interface = client_interface

 
    def list(self, file_path):
        """Not implemented for remote yet..."""
        raise NotImplementedError


