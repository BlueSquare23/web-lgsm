from pathlib import Path

def rename_file(file_path, new_name):
    """
    Rename a file

    Returns:
        bool: True if rename successful, False otherwise.
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return False

        new_path = path.parent / new_name
        path.rename(new_path)

        return True

    except Exception:
        return False
