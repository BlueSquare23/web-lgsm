import os

from flask import current_app

from app.utils.helpers import log_wrap
from .file_interface import FileInterface

class LocalFileInterface(FileInterface):
    """Interface for local file system operations"""
    def read_file(self, file_path):
        current_app.logger.info(log_wrap("file_path", file_path))
        try:
            with open(file_path) as f:
                return f.read()
        except Exception:
            return None
    
    def write_file(self, file_path, content):
        current_app.logger.info(log_wrap("file_path", file_path))
        
        # Check that file exists before allowing writes to it
        if not os.path.isfile(file_path):
            return False
        
        try:
            with open(file_path, "w") as f:
                f.write(content.replace("\r", ""))
            return True
        except Exception:
            return False
