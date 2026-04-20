import os
from pathlib import Path

def rename_file(file_path, new_name):
    """
    Rename a file

    Returns:
        bool: True if rename successful, False otherwise.
    """
    # Check that file exists before renaming it.
    if not os.path.isfile(file_path):
        return False

    try:
        file = Path(file_path)
        new_file = file.parent / new_name
        file.rename(new_file)
        return True

    except Exception as e:
        return False

