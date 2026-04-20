import logging

class FileInterface:
    """Base interface for file operations"""
    def __init__(self, server, logger=logging.getLogger(__name__)):
        self.server = server
        self.logger = logger
    
    def read(self, file_path):
        """Read file content - to be implemented by subclasses"""
        raise NotImplementedError
    
    def write(self, file_path, content):
        """Write content to file - to be implemented by subclasses"""
        raise NotImplementedError

    def delete(self, file_path):
        """Rename file - to be implemented by subclasses"""
        raise NotImplementedError

    def rename(self, file_path, new_name):
        """Rename file - to be implemented by subclasses"""
        raise NotImplementedError
