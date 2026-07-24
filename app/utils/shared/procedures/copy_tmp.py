import os
import shutil
import mimetypes
import tempfile

from pathlib import Path

from .traversal_safe import traversal_safe
from .is_excluded import is_excluded

MAX_DOWNLOAD_SIZE = 5 * 1024 * 1024  # 500MB

ALLOWED_MIME_PREFIXES = ('text/',)
ALLOWED_MIME_TYPES = (
    'application/json',
    'application/xml',
    'application/javascript',
    'application/x-yaml',
)


def copy_tmp(direction, real_path, tmp_path=None):
    """
    Relays file content between a local /tmp staging file and a real path on
    disk, so file content never has to travel over the RPC socket -- only
    the path strings do.

    direction='upload' (tmp_path -> real_path), used by write()

    direction='download' (real_path -> tmp_path), used by read()

    Returns:
        dict with keys: status, tmpfile, mime_type
    """
    if direction == 'upload':
        if not traversal_safe(real_path) or is_excluded(real_path):
            return {"status": "error", "mime_type": None}

        try:
            shutil.copyfile(tmp_path, real_path)
            return {"status": "success", "mime_type": None}
        except Exception as e:
            return {"status": "error", "error": str(e), "mime_type": None}

    if direction == 'download':
        tmp_fd, tmp_path = tempfile.mkstemp(dir="/tmp", prefix="web_lgsm_download_")
        os.close(tmp_fd)

        if not os.path.isfile(real_path) or not traversal_safe(real_path) or is_excluded(real_path):
            return {"status": "not_found", "tmpfile": tmp_path, "mime_type": None}

        if Path(real_path).stat().st_size > MAX_DOWNLOAD_SIZE:
            return {"status": "error", "tmpfile": tmp_path, "mime_type": None}

        mime_type, _ = mimetypes.guess_type(real_path)
        if mime_type is not None and not mime_type.startswith(ALLOWED_MIME_PREFIXES) and mime_type not in ALLOWED_MIME_TYPES:
            return {"status": "unsupported_type", "tmpfile": tmp_path, "mime_type": mime_type}

        try:
            shutil.copyfile(real_path, tmp_path)
            os.chmod(tmp_path, 0o640)
            shutil.chown(tmp_path, group="web-lgsm")
            return {"status": "success", "tmpfile": tmp_path, "mime_type": mime_type or "text/plain"}
        except Exception as e:
            return {"status": "error", "tmpfile": tmp_path, "error": str(e), "mime_type": None}

    return {"status": "error", "mime_type": None}

