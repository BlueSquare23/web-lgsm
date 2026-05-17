import os

from .traversal_safe import traversal_safe
from .is_excluded import is_excluded

def delete_file(file_path):
    """
    Share module delete file function.

    Returns:
        bool: True if delete successful, False otherwise.
    """
    # Check that file exists before trying to delete it.
    if not os.path.isfile(file_path):
        return False

    # Check file exists and path is allowed
    if not os.path.isfile(file_path) or not traversal_safe(file_path) or is_excluded(file_path):
        return False

    try:
        os.remove(file_path)
        return True

    except Exception as e:
        return False

