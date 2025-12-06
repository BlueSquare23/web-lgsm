import subprocess
import uuid
from flask import current_app
from .command_executor import BaseCommandExecutor

class LocalCommandExecutor(BaseCommandExecutor):
    """Local command execution using subprocess.Popen."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
    
    def run(self, cmd, cmd_id=None, app_context=False):
        """Execute command locally using subprocess.Popen."""
        if cmd_id is None:
            cmd_id = str(uuid.uuid4())
        
        proc_info = self._setup_proc_info(cmd_id)
        
        # Set lock flag to true.
        proc_info.process_lock = True
        
        # App context needed for logging in threads.
        if app_context:
            app_context.push()
        
        current_app.logger.info(self._log_wrap("cmd", cmd))
        
        # Subprocess call, Bytes mode, not buffered.
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
            text=False, bufsize=-1
        )
        
        proc_info.pid = proc.pid
        
        self.get_output(proc, proc_info, "stdout")
        self.get_output(proc, proc_info, "stderr")
        
        proc_info.exit_status = proc.wait()
        
        # Reset process_lock flag.
        proc_info.process_lock = False
        
        return proc_info
    
    def get_output(self, proc, proc_info, output_type):
        """Read output from subprocess."""
        while True:
            if output_type == "stdout":
                out_line = proc.stdout.read1().decode("utf-8")
            else:
                out_line = proc.stderr.read1().decode("utf-8")
            
            if not out_line:
                break
            
            self._process_raw_output(out_line, proc_info, output_type)
