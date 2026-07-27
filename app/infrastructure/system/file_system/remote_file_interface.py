import os

from app.infrastructure.system.ssh.client import SSHClientInterface

from app.utils.helpers import log_wrap
from .file_interface import FileInterface

class SSHFileInterface(FileInterface):
    """Interface for SSH/SFTP file operations"""

    def __init__(self, server, client_interface=SSHClientInterface()):
        super().__init__(server)
        self.client_interface = client_interface

    def read(self, file_path, download=False):
        """
        Returns:
            dict with keys: status, mime_type, data
        """
        self.logger.info(log_wrap("file_path", file_path))
        hostname = self.server.install_host
        username = self.server.username

        try:
            client = self.client_interface.get_client(username, hostname)

            with client.open_sftp() as sftp:
                with sftp.open(file_path, "r") as file:
                    content = file.read()

            return {
                'success': True,
                'mime_type': None,
                'data': content.decode()
            }

        except Exception as e:
            self.logger.debug(e)
            return {
                'success': False,
                'error': str(e),
                'mime_type': None,
                'data': None
            }
    
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
