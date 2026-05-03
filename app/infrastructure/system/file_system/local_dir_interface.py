import os
import getpass
import logging

from app.utils.helpers import log_wrap
from .dir_interface import DirInterface

class LocalDirInterface(DirInterface):
    """Interface for local file system operations"""

    USER = getpass.getuser()

    def __init__(self, server, executor):
        super().__init__(server)
        self.executor = executor


    def list(self, directory, show_hidden):
        self.logger.info(log_wrap("listing directory", directory))
        args = [ directory, show_hidden ]

        kwargs = dict()
        if self.server.username != LocalDirInterface.USER:
            kwargs = { 'as_user': self.server.username }

        return self.executor.call('list_dir', *args, **kwargs)

