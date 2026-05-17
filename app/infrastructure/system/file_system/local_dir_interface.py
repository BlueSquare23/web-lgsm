import os
import getpass
import logging

from app.utils.helpers import log_wrap
from .dir_interface import DirInterface

# TODO: This is mostly wiring and its a lotta samey wiring. Gotta be a better
# way to reduce redundant code.

class LocalDirInterface(DirInterface):
    """Interface for local file system operations"""

    USER = getpass.getuser()

    def __init__(self, server, executor):
        super().__init__(server)
        self.executor = executor

    def is_dir(self, path):
        args = [ path ]

        kwargs = dict()
        if self.server.username != LocalDirInterface.USER:
            kwargs = { 'as_user': self.server.username }

        return self.executor.call('is_dir', *args, **kwargs)

    def list(self, directory, show_hidden):
        self.logger.info(log_wrap("listing directory", directory))
        args = [ directory, show_hidden ]

        kwargs = dict()
        if self.server.username != LocalDirInterface.USER:
            kwargs = { 'as_user': self.server.username }

        resp = self.executor.call('list_dir', *args, **kwargs)
        self.logger.debug(log_wrap("rpc server resp", resp))
        return resp

    def traversal_safe(self, path):
        args = [ path ]

        kwargs = dict()
        if self.server.username != LocalDirInterface.USER:
            kwargs = { 'as_user': self.server.username }

        return self.executor.call('traversal_safe', *args, **kwargs)

    def check_excluded(self, path):
        args = [ path ]

        kwargs = dict()
        if self.server.username != LocalDirInterface.USER:
            kwargs = { 'as_user': self.server.username }

        return self.executor.call('is_excluded', *args, **kwargs)

