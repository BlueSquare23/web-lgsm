import os

from .local_file_interface import LocalFileInterface
from .remote_file_interface import SSHFileInterface

from app.infrastructure.system.user.user_module_service import UserModuleService
from app.utils.helpers import log_wrap

class FileManager:
    def __init__(self, executor=UserModuleService()):
        """
        Initialize FileManager with a server object.
        
        Args:
            server (GameServer): Game server object to manage files for
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
                self._interface = SSHFileInterface(self.server)
            else:
                self._interface = LocalFileInterface(self.server, self.executor)
        return self._interface
    
    def read(self, server, file_path):
        """
        Read a file from the server.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: File contents or None if failed
        """
        self.server = server
        return self.interface.read(file_path)
    
    def write(self, server, file_path, content):
        """
        Write content to a file on the server.
        
        Args:
            file_path (str): Path to the file
            content (str): Content to write
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.server = server
        return self.interface.write(file_path, content)

    def delete(self, server, file_path):
        """
        Delete a file on the server.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.server = server
        return self.interface.delete(file_path)

    def rename(self, server, file_path, new_name):
        """
        Rename a file on the server.
        
        Args:
            file_path (str): Path to the file
            new_name (str): New basename of file
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.server = server
        return self.interface.rename(file_path, new_name)

