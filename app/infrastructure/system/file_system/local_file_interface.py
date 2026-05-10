import os
import gzip
import base64
import getpass
import logging

from app.utils.helpers import log_wrap
from .file_interface import FileInterface

class LocalFileInterface(FileInterface):
    """Interface for local file system operations"""

    USER = getpass.getuser()

    def __init__(self, server, executor):
        super().__init__(server)
        self.executor = executor


    def _decompress(self, encoded_data):
        compressed_bytes = base64.b64decode(encoded_data)
        original_bytes = gzip.decompress(compressed_bytes)
        return original_bytes


    def read(self, file_path):
        """
        Reads local files via user module service read_file and auto decodes
        base64 content on successful reads.

        Returns:
            dict with keys: status, mime_type, data
        """
        self.logger.info(log_wrap("reading file_path", file_path))
        args = [ file_path ]

        kwargs = dict()
        if self.server.username != LocalFileInterface.USER:
            kwargs = { 'as_user': self.server.username }

        file = self.executor.call('read_file', *args, **kwargs)

        # Decompress and decode contents on success
        if file['status'] == 'success':
#            self.logger.debug(log_wrap("encoded", file['data']))
            try:
                text = self._decompress(file["data"]).decode("utf-8")
                file['data'] = text
            except:
                file['status'] = 'decompression_error'
                file['data'] = None

        return file


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
