import os
import logging

from .local_file_interface import LocalFileInterface
from .remote_file_interface import SSHFileInterface

from app.infrastructure.system.user.rpc_client import MultiUserRPCClient
from app.infrastructure.system.user.rpc_server_manager import MultiUserRPCServerManager

# TODO: Might be able to squeeze redundant code into the constructor.

class FileManager:
    def __init__(self, logger=logging.getLogger(__name__), executor=MultiUserRPCClient(), manager=MultiUserRPCServerManager()):
        """
        Initialize FileManager with a server object.
        
        Args:
            server (GameServer): Game server object to manage files for
        """
        self.server = None
        self._interface = None
        self.logger = logger
        self.executor = executor
        self.manager = manager

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

    def _check_thead(self):
        """
        Check and restart crashed threads.
        """
#        self.logger.debug(f"#################### SERVER USER {self.server.username}")
        self.manager.check(self.server.username)
    
    def read(self, server, file_path, download=False):
        """
        Read a file from the server.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: File contents or None if failed
        """
        self.server = server
        self._check_thead()
        return self.interface.read(file_path, download)
    
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
        self._check_thead()
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
        self._check_thead()
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
        self._check_thead()
        return self.interface.rename(file_path, new_name)

