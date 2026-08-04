import os
import shutil
import mimetypes
import tempfile

from pathlib import Path

from .traversal_safe import traversal_safe
from .is_excluded import is_excluded

# Only applies to files loaded into the in-browser editor (direct_download=False)
# Those get fully decoded into memory for the textarea. Actual file
# downloads are streamed straight from disk and have no such limit.
MAX_INLINE_VIEW_SIZE = 5 * 1024 * 1024  # 5MB

ALLOWED_MIME_PREFIXES = ('text/',)
ALLOWED_MIME_TYPES = (
    'application/json',
    'application/xml',
    'application/javascript',
    'application/x-yaml',
)

with open(f"{PLAYBOOKS}/app_conf.json") as f:
    app_conf = json.load(f)

APP_GROUP = app_conf["APP_GROUP"]

def copy_tmp(direction, real_path, tmp_path=None, direct_download=False):
    """
    Relays file content between a local /tmp staging file and a real path on
    disk, so file content never has to travel over the RPC socket -- only
    the path strings do.

    direction='upload' (tmp_path -> real_path), used by write()

    direction='download' (real_path -> tmp_path), used by read()

    Returns:
        dict with keys: success, error, tmpfile, mime_type
    """
    if direction == 'upload':
        if not traversal_safe(real_path) or is_excluded(real_path):
            return {"success": False, "error": "Permission denied", "mime_type": None}

        try:
            shutil.copyfile(tmp_path, real_path)
            return {"success": True, "mime_type": None}
        except Exception as e:
            return {"success": False, "error": str(e), "mime_type": None}

    if direction == 'download':
        tmp_fd, tmp_path = tempfile.mkstemp(dir="/tmp", prefix="web_lgsm_download_")
        os.close(tmp_fd)

        if not os.path.isfile(real_path) or not traversal_safe(real_path) or is_excluded(real_path):
            return {"success": False, "error": "Permission denied", "tmpfile": tmp_path, "mime_type": None}

        if not direct_download and Path(real_path).stat().st_size > MAX_INLINE_VIEW_SIZE:
            return {"success": False, "error": "File too large", "tmpfile": tmp_path, "mime_type": None}

        mime_type, _ = mimetypes.guess_type(real_path)

        if not direct_download:
            if mime_type is not None and not mime_type.startswith(ALLOWED_MIME_PREFIXES) and mime_type not in ALLOWED_MIME_TYPES:
                return {"success": False, "error": "Unsupported mime type", "tmpfile": tmp_path, "mime_type": mime_type}

        try:
            shutil.copyfile(real_path, tmp_path)
            os.chmod(tmp_path, 0o640)
            shutil.chown(tmp_path, group=APP_GROUP)
            return {"success": True, "tmpfile": tmp_path, "mime_type": mime_type or "text/plain"}
        except Exception as e:
            return {"success": False, "tmpfile": tmp_path, "error": str(e), "mime_type": None}

    return {"success": False, "mime_type": None}

