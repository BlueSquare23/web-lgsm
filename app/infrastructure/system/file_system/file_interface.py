class FileInterface:
    """Base interface for file operations"""
    def __init__(self, server):
        self.server = server
    
    def read_file(self, file_path):
        """Read file content - to be implemented by subclasses"""
        raise NotImplementedError
    
    def write_file(self, file_path, content):
        """Write content to file - to be implemented by subclasses"""
        raise NotImplementedError
