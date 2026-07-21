import os
import shutil
from .traversal_safe import traversal_safe
from .is_excluded import is_excluded

# TODO: MAKE RESPECT PERMISSION OF DEST FILE IF DEST FILE EXISTS!!!

def copy_from_tmp(tmp_path, dest_path):
    """
    Copies a staged temp file into dest_path as the target user.
    Called via RPC for cross-user uploads so the full file content
    never needs to travel over the socket.

    Returns:
        bool: True if successful, False otherwise.
    """
    if not traversal_safe(dest_path) or is_excluded(dest_path):
        return False

    try:
        shutil.copy(tmp_path, dest_path)
        return True

    except Exception as e:
        return False

