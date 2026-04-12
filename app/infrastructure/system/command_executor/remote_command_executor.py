import paramiko
import shlex
import time
import os

from app.infrastructure.system.repositories.proc_info_repo import InMemProcInfoRepository
from app.infrastructure.system.ssh.client import SSHClientInterface

from .base_executor import BaseCommandExecutor

class SshCommandExecutor(BaseCommandExecutor):
    """SSH command execution using paramiko."""
    
    def __init__(self, config, client_interface=SSHClientInterface()):
        super().__init__()
        self.config = config
        self.client_interface = client_interface
    
    def run(self, cmd, cmd_id=None, app_context=False, timeout=5.0, server=None):
        """Execute command via SSH."""
        if server is None:
            raise ValueError("server parameter is required for SSH execution")
        
        if cmd_id is None:
            cmd_id = server.id
        
        proc_info = InMemProcInfoRepository().get(cmd_id, create=True)

        if self.config.getboolean('settings', 'clear_output_on_reload'):
            proc_info.stdout.clear()
            proc_info.stderr.clear()
        
        hostname = server.install_host
        username = server.username

        # App context needed for logging in threads.
        if app_context:
            app_context.push()

        safe_cmd = shlex.join(cmd)
        
        # Log info.
        self.logger.debug(self._log_wrap("proc_info pre ssh cmd:", str(proc_info)))
        self.logger.info(cmd)
        self.logger.info(safe_cmd)
        self.logger.info(hostname)
        self.logger.info(username)

        try:
            client = self.client_interface.get_client(username, hostname)

            proc_info.process_lock = True
            # Open a new session and request a PTY.
            channel = client.get_transport().open_session()
            channel.set_combine_stderr(False)
            channel.exec_command(safe_cmd)

            # Optionally set timeout (if provided).
            if timeout:
                channel.settimeout(timeout)

            self._read_ssh_output(channel, proc_info)

            # Wait for the command to finish and get the exit status.
            proc_info.exit_status = channel.recv_exit_status()
            proc_info.process_lock = False
            return True

        except paramiko.SSHException as e:
            self.logger.debug(str(e))
            proc_info.stderr.append(str(e))
            proc_info.exit_status = 5
            proc_info.process_lock = False
            return False

        except TimeoutError as e:
            self.logger.debug(str(e))
            proc_info.stderr.append(str(e))
            proc_info.exit_status = 7
            proc_info.process_lock = False
            return False
    
    def get_output(self, proc, proc_info, output_type):
        """
        SSH implementation doesn't use this method directly because 
        output reading happens differently with paramiko channels.
        """
        raise NotImplementedError("SSH executor uses _read_ssh_output instead")
    
    def _read_ssh_output(self, channel, proc_info):
        """Read output from SSH channel."""
        
        while True:
            # Read stdout if data is available.
            if channel.recv_ready():
                stdout_chunk = channel.recv(8192).decode("utf-8")
                self._process_ssh_chunk(stdout_chunk, proc_info, "stdout")

            if channel.recv_stderr_ready():
                stderr_chunk = channel.recv_stderr(8192).decode("utf-8")
                self._process_ssh_chunk(stderr_chunk, proc_info, "stderr")

            # Break the loop if the command has finished.
            if channel.exit_status_ready():
                # Ensure any remaining stderr and stdout are captured.
                while channel.recv_stderr_ready():
                    stderr_chunk = channel.recv_stderr(8192).decode("utf-8")
                    self._process_ssh_chunk(stderr_chunk, proc_info, "stderr")

                while channel.recv_ready():
                    stdout_chunk = channel.recv(8192).decode("utf-8")
                    self._process_ssh_chunk(stdout_chunk, proc_info, "stdout")

                break

            # Keep CPU from burning.
            time.sleep(0.1)
    
    def _process_ssh_chunk(self, chunk, proc_info, output_type):
        """Process a chunk of SSH output."""
        if not chunk:
            return
        
        lines = chunk.splitlines(keepends=True)
        for line in lines:
            if line == "\r\n":
                continue
            
            # Skip duplicates
#            if output_type == "stdout" and line in proc_info.stdout:
#                continue
            if output_type == "stderr" and line in proc_info.stderr:
                continue
            
            # Add newlines if configured
            if self.config.getboolean('settings', 'end_in_newlines'):
                if not (line.endswith("\n") or line.endswith("\r")):
                    line += "\n"
            
            # Add to appropriate output list
            if output_type == "stdout":
                proc_info.stdout.append(line)
            else:
                proc_info.stderr.append(line)
            
            # Log
            log_msg = self._log_wrap(output_type, line.strip())
            self.logger.debug(log_msg)
