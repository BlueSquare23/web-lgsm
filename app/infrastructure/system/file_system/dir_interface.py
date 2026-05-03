import logging

class DirInterface:
    """Base interface for dir operations"""
    def __init__(self, server, logger=logging.getLogger(__name__)):
        self.server = server
        self.logger = logger
    
    def list(self, file_path):
        """List dir contents - to be implemented by subclasses"""
        raise NotImplementedError
    
