import logging

class DirInterface:
    """Base interface for dir operations"""
    def __init__(self, server, logger=logging.getLogger(__name__)):
        self.server = server
        self.logger = logger

    def is_dir(self, server, path):
        """Check path is a directory - to be implemented by subclasses"""
        raise NotImplementedError
    
    def list(self, server, path):
        """List dir contents - to be implemented by subclasses"""
        raise NotImplementedError

    def traversal_safe(self, server, file_path):
        """check traversal attempts - to be implemented by subclasses"""
        raise NotImplementedError
    
    def check_excluded(self, server, file_path):
        """check excluded files/dirs - to be implemented by subclasses"""
        raise NotImplementedError
