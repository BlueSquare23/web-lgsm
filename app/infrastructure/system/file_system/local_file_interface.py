import os
import getpass
import base64
import logging

from app.utils.helpers import log_wrap
from .file_interface import FileInterface

class LocalFileInterface(FileInterface):
    """Interface for local file system operations"""

    USER = getpass.getuser()

    def __init__(self, server, executor):
        super().__init__(server)
        self.executor = executor


    def read(self, file_path):
        self.logger.info(log_wrap("file_path", file_path))
        args = [ file_path ]

        kwargs = dict()
        if self.server.username != LocalFileInterface.USER:
            kwargs = { 'as_user': self.server.username }

        encoded = self.executor.call('read_file', *args, **kwargs)
        if not encoded:
            return None

        stripped = encoded.strip()
        if stripped == 'null':
            return None

        self.logger.debug(log_wrap("encoded", encoded))
        
        return base64.b64decode(encoded).decode('utf-8', errors='ignore')


    def write(self, file_path, content):
        self.logger.info(log_wrap("file_path", file_path))

        # Encode the str to bytes.
        encoded_bytes = content.encode('utf-8')

        # Encode the bytes to base64 str.
        encoded_content = base64.b64encode(encoded_bytes).decode('utf-8')

        args = [ file_path, encoded_content ]

        kwargs = dict()
        if self.server.username != LocalFileInterface.USER:
            kwargs = { 'as_user': self.server.username }

        return self.executor.call('write_file', *args, **kwargs)


    def delete(self, file_path):
        self.logger.info(log_wrap("file_path", file_path))

        args = [ file_path ]

        kwargs = dict()
        if self.server.username != LocalFileInterface.USER:
            kwargs = { 'as_user': self.server.username }

        return self.executor.call('delete_file', *args, **kwargs)
