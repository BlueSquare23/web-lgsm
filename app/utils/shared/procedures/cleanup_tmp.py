from pathlib import Path

def cleanup_tmp(tmp_path):
    """
    Cleanup tempfiles after copy.

    Returns:
        bool: True if successful, False otherwise.
    """
    
    parent_dir = Path("/tmp")
    child_path = Path(tmp_path)

    # Reject unless under /tmp
    if not child_path.is_relative_to(parent_dir):
        return False

    try:
        child_path.unlink()
        return True

    except Exception as e:
        return False

