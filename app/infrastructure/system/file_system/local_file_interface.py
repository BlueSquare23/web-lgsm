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
        self.logger.info(log_wrap("reading file_path", file_path))
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
        """byte-safe file writer"""
        self.logger.info(log_wrap("writing file_path", file_path))

        # Accept both str and bytes
        if isinstance(content, str):
            content_bytes = content.encode("utf-8")
        else:
            content_bytes = content  # already bytes

        encoded_content = base64.b64encode(content_bytes).decode("utf-8")

        args = [ file_path, encoded_content ]

        kwargs = dict()
        if self.server.username != LocalFileInterface.USER:
            kwargs = { 'as_user': self.server.username }

        return self.executor.call('write_file', *args, **kwargs)


    def delete(self, file_path):
        self.logger.info(log_wrap("deleting file_path", file_path))

        args = [ file_path ]

        kwargs = dict()
        if self.server.username != LocalFileInterface.USER:
            kwargs = { 'as_user': self.server.username }

        return self.executor.call('delete_file', *args, **kwargs)

    def rename(self, file_path, new_name):
        self.logger.info(log_wrap("renaming file_path", file_path))

        args = [ file_path, new_name ]

        kwargs = dict()
        if self.server.username != LocalFileInterface.USER:
            kwargs = { 'as_user': self.server.username }

        return self.executor.call('rename_file', *args, **kwargs)
