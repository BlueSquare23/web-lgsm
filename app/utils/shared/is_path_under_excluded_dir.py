from .exclude_matches import matches
from pathlib import Path

def is_path_under_excluded_dir(path, dir_exact, dir_globs):
    """
    Checks if supplied path str falls below one of the excluded dirs.

    Uses pathlib to prevent traversal attempts.
    """
    p = Path(path)

    for parent in [p] + list(p.parents):
        parent_str = str(parent)

        if matches(parent_str, dir_exact, dir_globs):
            return True

    return False

