import os
import shutil
from .traversal_safe import traversal_safe
from .is_excluded import is_excluded

def move_from_tmp(tmp_path, dest_path):
    """
    Moves a staged temp file into dest_path as the target user.
    Called via RPC for cross-user uploads so the full file content
    never needs to travel over the socket.

    Returns:
        bool: True if successful, False otherwise.
    """
    if not traversal_safe(dest_path) or is_excluded(dest_path):
        # Don't leave the temp file around on a security rejection
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        return False

    try:
        shutil.move(tmp_path, dest_path)
        return True
    except Exception:
        return False
    finally:
        # Belt-and-suspenders: clean up if move failed and file still exists
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
