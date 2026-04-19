import os

def delete_file(file_path):
    """
    Share module delete file function.

    Returns:
        bool: True if delete successful, False otherwise.
    """
    # Check that file exists before trying to delete it.
    if not os.path.isfile(file_path):
        return False

    try:
        os.remove(file_path)
        return True

    except Exception as e:
        return False

