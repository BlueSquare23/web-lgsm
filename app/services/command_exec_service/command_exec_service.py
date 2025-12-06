from .local_command_executor import LocalCommandExecutor

class CommandExecService:
    """Service for command execution with dependency injection."""
    
    def __init__(self, config):
        self.config = config
        self._executors = {}
    
    def get_local_executor(self):
        """Get local command executor."""
        if 'local' not in self._executors:
            self._executors['local'] = LocalCommandExecutor(self.config)
        return self._executors['local']
    
    def get_executor(self, server_type='local'):
        """Get executor based on server type."""
        if server_type == 'local':
            return self.get_local_executor()
        elif server_type == 'ssh':
            # This will be implemented later for SSH
            raise NotImplementedError("SSH executor not implemented yet")
        else:
            raise ValueError(f"Unknown server type: {server_type}")
