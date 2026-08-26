import os
import gzip
import base64
import getpass
import logging
import shutil
import tempfile
import subprocess  # For facls via shell. Slow, might replace w/ pylibacl.

from app.utils.helpers import log_wrap
from app.utils.paths import PATHS
from .file_interface import FileInterface
from .utils import is_utf8_decodable

class LocalFileInterface(FileInterface):
    """Interface for local file system operations"""

    USER = getpass.getuser()

    def __init__(self, server, client):
        super().__init__(server)
        self.client = client

    def _rpc_kwargs(self):
        if self.server.username == LocalFileInterface.USER:
            return {}
        return {'as_user': self.server.username}

    def read(self, file_path, download):
        """
        Reads local files via multi user rpc service.

        When download=True, the file's contents are never loaded into memory:
        the tmp file staged by copy_tmp is left in place and handed back via
        result['tmpfile'] so the caller can stream it straight to the client
        (e.g. Flask's send_file), then clean it up itself once the response
        has actually been sent via cleanup_download().

        Returns:
            dict with keys: success, error, mime_type, data (only when
            download=False), tmpfile
        """
        self.logger.info(log_wrap("reading file_path", file_path))

        kwargs = self._rpc_kwargs()
        tmp_path = None
        keep_tmp = False

        try:
            result = self.client.call('copy_tmp', 'download', file_path, None, download, **kwargs)
            self.logger.debug(result)

            tmp_path = result.get('tmpfile')

            if not result.get('success'):
                return result

            if download:
                # Caller owns tmp_path from here on and is responsible for
                # calling cleanup_download() once it's done streaming.
                keep_tmp = True
                return result

            with open(tmp_path, 'rb') as f:
                if is_utf8_decodable(tmp_path):
                    result['data'] = f.read().decode('utf-8')
                    result['decodable'] = True
                else:
                    result['data'] = f.read()
                    result['decodable'] = False

            return result

        except Exception as e:
            result = {"success": False, "error": str(e), "mime_type": None}
            return result

        finally:
            if tmp_path and not keep_tmp:
                self.client.call('cleanup_tmp', tmp_path, **kwargs)  # whoever created it, deletes it

    def cleanup_download(self, tmp_path):
        """
        Deletes a tmp file previously staged by read(file_path, download=True)
        once the caller is done streaming it to the client.
        """
        self.logger.info(log_wrap("cleaning up download tmp_path", tmp_path))
        return self.client.call('cleanup_tmp', tmp_path, **self._rpc_kwargs())

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
                    content = content.replace('\r\n', '\n')
                    tmp_file.write(content.encode("utf-8"))
                elif isinstance(content, (bytes, bytearray)):
                    tmp_file.write(content)
                else:
                    # File-like stream: copy in 256KB chunks, never fully buffered
                    shutil.copyfileobj(content, tmp_file, length=256 * 1024)

            # Use acls to ensure temp file is readable by target user.
            os.chmod(tmp_path, 0o600)
            subprocess.run([PATHS["setfacl"], "-m", f"u:{self.server.username}:r", tmp_path], check=True)

            result = self.client.call('copy_tmp', 'upload', file_path, tmp_path, **self._rpc_kwargs())
            self.logger.debug(result)
            return result.get('success')
        finally:
            # Tmp file is always ours (we staged it), so we always clean it up ourselves.
            self.client.call('cleanup_tmp', tmp_path)

    def delete(self, file_path):
        self.logger.info(log_wrap("deleting file_path", file_path))

        args = [ file_path ]
        kwargs = self._rpc_kwargs()

        return self.client.call('delete_file', *args, **kwargs)

    def rename(self, file_path, new_name):
        self.logger.info(log_wrap("renaming file_path", file_path))

        args = [ file_path, new_name ]
        kwargs = self._rpc_kwargs()

        return self.client.call('rename_file', *args, **kwargs)
