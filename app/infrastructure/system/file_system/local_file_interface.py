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
        self.logger.info(log_wrap("FILE", file))

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
        """
        Byte-safe file writer. Accepts str, bytes, or a file-like stream.

        Same-user path: writes raw bytes directly via write_file_bytes,
        no base64 encoding needed.

        Cross-user path: streams content into a temp file, then sends
        only the path over the socket via move_from_tmp. The full file
        content never travels through JSON or the socket.
        """
        self.logger.info(log_wrap("writing file_path", file_path))

        same_user = (self.server.username == LocalFileInterface.USER)

        if same_user:
            # Direct call, no socket, no encoding overhead.
            # Normalize to bytes first; for streams read them here since
            # write_file_bytes takes bytes, not a file-like.
            if isinstance(content, str):
                content_bytes = content.encode("utf-8")
            elif isinstance(content, (bytes, bytearray)):
                content_bytes = content
            else:
                # File-like stream
                content_bytes = content.read()

            return self.executor.call('write_file_bytes', file_path, content_bytes)

        # Cross-user path: stage to temp file, pass only the path over the socket.
        # We never base64-encode the content at all.
        tmp_fd, tmp_path = tempfile.mkstemp(dir="/tmp", prefix="wlgsm_upload_")
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

            copy_result = self.executor.call('copy_from_tmp', tmp_path, file_path, as_user=self.server.username)
            cleanup_result = self.executor.call('cleanup_tmp', tmp_path, as_user=LocalFileInterface.USER)

            self.logger.info(log_wrap("############ COPY RESULT", copy_result))
            self.logger.info(log_wrap("############ CLEANUP RESULT", cleanup_result))

            if copy_result and cleanup_result:
                return True
            else:
                return False
            
#            return self.executor.call('move_from_tmp', tmp_path, file_path, as_user=self.server.username)

        except Exception:
            # Clean up temp file if we never got to send it
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
            raise

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
