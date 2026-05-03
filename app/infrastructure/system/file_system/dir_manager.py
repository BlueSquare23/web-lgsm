import os

from .local_dir_interface import LocalDirInterface
from .remote_dir_interface import SSHDirInterface

from app.infrastructure.system.user.user_module_service import UserModuleService
from app.utils.helpers import log_wrap

class DirectoryManager:
    def __init__(self, executor=UserModuleService()):
        """
        Initialize DirectoryManager with a server object.
        
        Args:
            server (GameServer): Game server object to manage dir for
        """
        self.server = None
        self._interface = None
        self.executor = executor
        
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
                self._interface = LocalDirInterface(self.server, self.executor)
        return self._interface
    
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

