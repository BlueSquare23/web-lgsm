import os
import paramiko

from flask import current_app
from functools import lru_cache

from app.utils.helpers import log_wrap
from .file_interface import FileInterface

class SSHFileInterface(FileInterface):
    """Interface for SSH/SFTP file operations"""

    # TODO: These two functions are shared with the SshCommandExecutor class as
    # well. So they need abstracted even further and put into their own ssh
    # access class.
    def _get_ssh_key_file(self, user, host):
        """
        Fetches ssh private key file for user:host from ~/.ssh if user:host key
        exists.
        """
        home_dir = os.path.expanduser("~")
        ssh_dir = os.path.join(home_dir, ".ssh")
        if not os.path.isdir(ssh_dir):
            os.mkdir(ssh_dir, mode=0o700)

        all_pub_keys = [f for f in os.listdir(ssh_dir) if f.endswith(".pub")]

        key_name = f"id_ecdsa_{user}_{host}"

        # If no key files for user@server yet, create new one.
        if key_name + ".pub" not in all_pub_keys:
            return None

        keyfile = os.path.join(ssh_dir, key_name)
        return keyfile

    @lru_cache(maxsize=32)
    def _get_ssh_client(self, hostname, username, key_filename):
        """
        Cache ssh connection objects using lru_cache.
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname, 
            username=username,
            key_filename=key_filename,
            timeout=3,
            look_for_keys=False, 
            allow_agent=False
        )

        # Verify connection is alive.
        try:
            client.exec_command("echo 'healthcheck'", timeout=2)
            return client
        except Exception:
            client.close()
            raise

    def read_file(self, file_path):
        current_app.logger.info(log_wrap("file_path", file_path))
        pub_key_file = self._get_ssh_key_file(self.server.username, self.server.install_host)
        hostname = self.server.install_host
        username = self.server.username
        
        try:
            client = self._get_ssh_client(hostname, username, pub_key_file)
            
            with client.open_sftp() as sftp:
                with sftp.open(file_path, "r") as file:
                    content = file.read()
            
            return content.decode()
        except Exception as e:
            current_app.logger.debug(e)
            return None
    
    def write_file(self, file_path, content):
        current_app.logger.info(log_wrap("file_path", file_path))
        pub_key_file = self._get_ssh_key_file(self.server.username, self.server.install_host)
        hostname = self.server.install_host
        username = self.server.username
        
        try:
            client = self._get_ssh_client(hostname, username, pub_key_file)
            
            with client.open_sftp() as sftp:
                with sftp.open(file_path, "w") as file:
                    file.write(content.replace("\r", ""))
            
            return True
        except Exception as e:
            current_app.logger.debug(e)
            return False
