import os

def is_dir(path):
    """
    Checks if is a directory.
    """
    if os.path.isabs(path) and os.path.isdir(path):
        return True

    return False

