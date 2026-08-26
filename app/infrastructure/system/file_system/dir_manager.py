import os

from .local_dir_interface import LocalDirInterface
from .remote_dir_interface import SSHDirInterface

from app.infrastructure.system.user.rpc_supervisor import MultiUserRPCSupervisor
from app.utils.helpers import log_wrap

class DirectoryManager():
    def __init__(self, client=MultiUserRPCSupervisor()):
        """
        Initialize DirectoryManager with a server object.
        
        Args:
            server (GameServer): Game server object to manage dir for
        """
        self.server = None
        self._interface = None
        self.client = client
        
    @property
    def interface(self):
        """
        Get the appropriate interface (local or SSH) based on the server.
        Uses lazy initialization to create the interface only when needed.
        """
        if self._interface is None:
            if self.server.install_type == 'remote':
                self._interface = SSHDirInterface(self.server)
            else:
                self._interface = LocalDirInterface(self.server, self.client)
        return self._interface

    def is_dir(self, server, path):
        """
        Checks if path is a directory.
        
        Args:
            server (GameServer): GameServer object
            path (str): Path to check is a directory
            
        Returns:
            bool: True if is dir, False otherwise.
        """
        self.server = server
        return self.interface.is_dir(path)
    
    def list(self, server, directory, show_hidden):
        """
        List the contents of a directory.
        
        Args:
            server (GameServer): GameServer object
            directory (str): Path to directory to list
            show_hidden (bool): To show hidden files or not
            
        Returns:
            list: List of file info dicts
        """
        self.server = server
        return self.interface.list(directory, show_hidden)

    def traversal_safe(self, server, path):
        """
        Checks if file or directory path is above game server users home
        directory.

        Args:
            server (GameServer): GameServer object
            path (str): Path to directory or file to check 

        """
        self.server = server
        return self.interface.traversal_safe(path)

    def check_excluded(self, server, path):
        """
        Checks if file or directory path is excluded.

        Args:
            server (GameServer): GameServer object
            path (str): Path to directory or file to check 
        """
        self.server = server
        return self.interface.check_excluded(path)
        
