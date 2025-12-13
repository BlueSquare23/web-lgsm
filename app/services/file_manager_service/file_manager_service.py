import os

from .local_file_interface import LocalFileInterface
from .remote_file_interface import SSHFileInterface
from app.utils.helpers import log_wrap

class FileManagerService:
    def __init__(self, server):
        """
        Initialize FileManagerService with a server object.
        
        Args:
            server (GameServer): Game server object to manage files for
        """
        self.server = server
        self._interface = None
        
    @property
    def interface(self):
        """
        Get the appropriate interface (local or SSH) based on the server.
        Uses lazy initialization to create the interface only when needed.
        """
        if self._interface is None:
            if self.server.install_type == 'remote':
                self._interface = SSHFileInterface(self.server)
            else:
                self._interface = LocalFileInterface(self.server)
        return self._interface
    
    def read_file(self, file_path):
        """
        Read a file from the server.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: File contents or None if failed
        """
        return self.interface.read_file(file_path)
    
    def write_file(self, file_path, content):
        """
        Write content to a file on the server.
        
        Args:
            file_path (str): Path to the file
            content (str): Content to write
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.interface.write_file(file_path, content)
    
    def download_file(self, file_path):
        """
        Download a file from the server.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            Flask response: File download response
        """
        from flask import send_file, send_from_directory, current_app
        import io
        
        file_contents = self.read_file(file_path)
        if file_contents is None:
            from flask import flash, redirect, url_for
            flash("Problem retrieving file contents", category="error")
            return redirect(url_for("main.home"))
        
        filename = os.path.basename(file_path)
        
        if self.server.install_type == 'remote':
            file_like_object = io.BytesIO(file_contents.encode("utf-8"))
            return send_file(
                file_like_object,
                as_attachment=True,
                download_name=filename,
                mimetype="text/plain",
            )
        
        basedir, basename = os.path.split(file_path)
        current_app.logger.info(log_wrap("basedir", basedir))
        current_app.logger.info(log_wrap("basename", basename))
        return send_from_directory(basedir, basename, as_attachment=True)
    
