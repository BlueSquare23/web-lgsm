from pathlib import Path

def traversal_safe(path):
    """
    General purpose is traversal attempt checker.

    Returns:
        bool: True if NOT dir traversal attempt. In other words True if 
              valid path, False otherwise.
    """
    current_home = Path.home()
    base_dir = Path(current_home).resolve()
    candidate = (base_dir / path).resolve()

    try:
        candidate.relative_to(base_dir)
    except ValueError:
        return False

    return True

