import os
import gzip
import base64
import getpass
import logging
import shutil
import tempfile

from app.utils.helpers import log_wrap
from .file_interface import FileInterface

class LocalFileInterface(FileInterface):
    """Interface for local file system operations"""

    USER = getpass.getuser()

    def __init__(self, server, executor):
        super().__init__(server)
        self.executor = executor

    def _rpc_kwargs(self):
        if self.server.username == LocalFileInterface.USER:
            return {}
        return {'as_user': self.server.username}

    def read(self, file_path):
        """
        Reads local files via multi user rpc service.

        Returns:
            dict with keys: success, error, mime_type, data
        """
        self.logger.info(log_wrap("reading file_path", file_path))

        kwargs = self._rpc_kwargs()
        tmp_path = None

        try:
            result = self.executor.call('copy_tmp', 'download', file_path, **kwargs)
            self.logger.debug(result)

            if not result.get('success'):
                return result

            tmp_path = result.get('tmpfile')

            with open(tmp_path, 'rb') as f:
                result['data'] = f.read().decode('utf-8')
            return result

        except Exception as e:
            result = {"success": False, "error": str(e), "mime_type": None}
            return result

        finally:
            if tmp_path:
                self.executor.call('cleanup_tmp', tmp_path, **kwargs)  # whoever created it, deletes it

    def write(self, file_path, content):
        """
        Byte-safe file writer. Accepts str, bytes, or a file-like stream.

        Streams content into a temp file, then sends only the path over the
        socket via move_from_tmp. The full file content never travels through 
        JSON or the socket.
        """
        self.logger.info(log_wrap("writing file_path", file_path))

        tmp_fd, tmp_path = tempfile.mkstemp(dir="/tmp", prefix="web_lgsm_upload_")
        try:
            with os.fdopen(tmp_fd, 'wb') as tmp_file:
                if isinstance(content, str):
                    tmp_file.write(content.encode("utf-8"))
                elif isinstance(content, (bytes, bytearray)):
                    tmp_file.write(content)
                else:
                    # File-like stream: copy in 256KB chunks, never fully buffered
                    shutil.copyfileobj(content, tmp_file, length=256 * 1024)

            # Temp file must be readable by the daemon running as the target user
            os.chmod(tmp_path, 0o644)

            result = self.executor.call('copy_tmp', 'upload', file_path, tmp_path, **self._rpc_kwargs())
            self.logger.debug(result)
            return result.get('success')
        finally:
            # Tmp file is always ours (we staged it), so we always clean it up ourselves.
            self.executor.call('cleanup_tmp', tmp_path)

    def delete(self, file_path):
        self.logger.info(log_wrap("deleting file_path", file_path))

        args = [ file_path ]
        kwargs = self._rpc_kwargs()

        return self.executor.call('delete_file', *args, **kwargs)

    def rename(self, file_path, new_name):
        self.logger.info(log_wrap("renaming file_path", file_path))

        args = [ file_path, new_name ]
        kwargs = self._rpc_kwargs()

        return self.executor.call('rename_file', *args, **kwargs)
