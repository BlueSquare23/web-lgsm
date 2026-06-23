import os
import shutil

from .traversal_safe import traversal_safe
from .is_excluded import is_excluded

def delete_file(file_path):
    """
    Share module delete file function.

    Returns:
        bool: True if delete successful, False otherwise.
    """
    # Check path is allowed
    if not traversal_safe(file_path) or is_excluded(file_path):
        return False

    try:
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)  # recursive delete
            return True

        os.remove(file_path)
        return True

    except Exception as e:
        return False

