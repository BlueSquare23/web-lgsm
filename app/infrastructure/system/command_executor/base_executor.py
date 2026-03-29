import logging

from abc import ABC, abstractmethod

from app.infrastructure.system.repositories.proc_info_repo import InMemProcInfoRepository

class CommandExecutor(ABC):
    """Abstract base class for command execution."""
    
    @abstractmethod
    def run(self, cmd, cmd_id=None, app_context=False):
        """Execute a command and return process info."""
        pass
    
    @abstractmethod
    def get_output(self, proc, proc_info, output_type):
        """Get output from process."""
        pass


class BaseCommandExecutor(CommandExecutor):
    """Base implementation with common functionality."""
    
    def __init__(self, logger=logging.getLogger(__name__)):
        self.config = None  # Will be injected
        self.proc_info_repo = None  # Will be injected
        self.logger = logger
        
    def _setup_proc_info(self, cmd_id, create=True):
        """Setup process info object."""
        if not self.proc_info_repo:
            self.proc_info_repo = InMemProcInfoRepository()
        
        proc_info = self.proc_info_repo.get(cmd_id, create=create)
        
        if self.config.getboolean('settings', 'clear_output_on_reload'):
            proc_info.stdout.clear()
            proc_info.stderr.clear()
        
        return proc_info
    
    def _process_output_line(self, line, output_type, proc_info):
        """Process a single line of output."""
        # Add the newlines for optional old-style setting.
        if self.config.getboolean('settings', 'end_in_newlines'):
            if not line.endswith("\n"):
                line = line + "\n"
        
        if output_type == "stdout":
            proc_info.stdout.append(line)
            log_msg = self._log_wrap("stdout", line.replace("\n", ""))
            self.logger.debug(log_msg)
        else:
            proc_info.stderr.append(line)
            log_msg = self._log_wrap("stderr", line.replace("\n", ""))
            self.logger.debug(log_msg)
    
    def _log_wrap(self, stream_type, message):
        """Wrapper for logging (assuming this exists somewhere)."""
        # TODO: This should be imported from utils 
        return f"[{stream_type}] {message}"
    
    def _process_raw_output(self, raw_line, proc_info, output_type):
        """Process raw output line with carriage return/newline handling."""
        if not raw_line:
            return
        
        for rline in raw_line.split("\r"):
            if rline == "":
                continue
            
            # Add back in carriage returns, ignoring lines terminated with a newline.
            if not rline.endswith("\r") and not rline.endswith("\n"):
                rline = rline + "\r"
            
            for line in rline.split("\n"):
                if line == "":
                    continue
                
                # Add back in newlines, ignoring lines terminated with a carriage return.
                if not line.endswith("\n") and not line.endswith("\r"):
                    line = line + "\n"
                
                self._process_output_line(line, output_type, proc_info)
