import getpass
from .local_command_executor import LocalCommandExecutor
from .remote_command_executor import SshCommandExecutor
from app.utils.paths import PATHS
from app.models import GameServer

class CommandExecService:
    """Service for command execution with dependency injection."""
    USER = getpass.getuser()
    
    def __init__(self, config):
        self.config = config
        self._executors = {}
    
    def get_local_executor(self):
        """Get local command executor."""
        if 'local' not in self._executors:
            self._executors['local'] = LocalCommandExecutor(self.config)
        return self._executors['local']
    
    def get_ssh_executor(self):
        """Get SSH command executor."""
        if 'ssh' not in self._executors:
            self._executors['ssh'] = SshCommandExecutor(self.config)
        return self._executors['ssh']
    
    def get_executor(self, server_type='local', **kwargs):
        """Get executor based on server type."""
        if server_type == 'local':
            return self.get_local_executor()
        elif server_type == 'remote':
            return self.get_ssh_executor()
        else:
            raise ValueError(f"Unknown server type: {server_type}")
    
    def run_command(self, cmd, server=None, cmd_id=None, app_context=False, 
                   timeout=None, **kwargs):
        """
        Unified command execution interface.
        
        Args:
            cmd (list): Command to execute
            server (GameServer): Server object (required for ssh command)
            cmd_id (str): Optional command ID
            app_context: Flask app context for threads
            timeout: Command timeout
            **kwargs: Additional executor-specific arguments
        
        Returns:
            Process info or boolean result  (TODO: Make just bool, proc_info should all go in ProcInfoService singleton and fetched via IDs)
        """

        args = {
            "cmd": cmd, 
            "cmd_id": cmd_id,
            "app_context": app_context,
            "timeout": timeout,
            **kwargs
        }

        if server is None:
            args["server"] = None
            executor = self.get_local_executor()
        else:
            assert isinstance(server, GameServer), "server is not an instance of GameServer"
            executor = self.get_executor(server.install_type)

        # Prepend sudo stuff for local non-same user installs.
        if server.install_type == 'local' and server.username != CommandExecService.USER:
            cmd = [
                PATHS["sudo"],
                "-n",
                "-u",
                server.username,
            ] + cmd
                
        # Prepend docker stuff.
        if server.install_type == 'docker':
            cmd = [
                PATHS["sudo"],
                "-n",
                PATHS["docker"],
                "exec",
                "--user",
                server.username,
                server.script_name,
            ] + cmd
 
        return executor.run(**args)

