import os
from .traversal_safe import traversal_safe
from .is_excluded import is_excluded

def write_file_bytes(file_path, content_bytes):
    """
    Writes raw bytes directly to file_path. Used for same-user writes
    where base64 encoding is unnecessary overhead.

    Returns:
        bool: True if write successful, False otherwise.
    """
    if not traversal_safe(file_path) or is_excluded(file_path):
        return False

    try:
        with open(file_path, "wb") as f:
            f.write(content_bytes)
        return True
    except Exception:
        return False
