import os

from app.infrastructure.system.ssh.client import SSHClientInterface

from app.utils.helpers import log_wrap
from .file_interface import FileInterface

class SSHFileInterface(FileInterface):
    """Interface for SSH/SFTP file operations"""

    def __init__(self, server, client_interface=SSHClientInterface()):
        super().__init__(server)
        self.client_interface = client_interface

    def read(self, file_path):
        self.logger.info(log_wrap("file_path", file_path))
        hostname = self.server.install_host
        username = self.server.username
        
        try:
            client = self.client_interface.get_client(username, hostname)
            
            with client.open_sftp() as sftp:
                with sftp.open(file_path, "r") as file:
                    content = file.read()
            
            return content.decode()
        except Exception as e:
            self.logger.debug(e)
            return None
    
    def write(self, file_path, content):
        self.logger.info(log_wrap("file_path", file_path))
        hostname = self.server.install_host
        username = self.server.username
        
        try:
            client = self.client_interface.get_client(username, hostname)
            
            with client.open_sftp() as sftp:
                with sftp.open(file_path, "w") as file:
                    file.write(content.replace("\r", ""))
            
            return True
        except Exception as e:
            self.logger.debug(e)
            return False
