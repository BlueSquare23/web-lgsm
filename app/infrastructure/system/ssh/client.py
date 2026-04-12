import os
import paramiko

from functools import lru_cache

class SSHClientInterface:

    @lru_cache(maxsize=32)
    def get_client(self, username, hostname):
        """
        Cache ssh connection objects using lru_cache.
        """
        keyfile = self._get_ssh_key_file(username, hostname)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname, 
            username=username,
            key_filename=keyfile,
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

