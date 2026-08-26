import os
from .matches import matches
from .load_exclusions import load_exclusions
from .is_path_under_excluded_dir import is_path_under_excluded_dir

def is_excluded(path):
    """
    General purpose is excluded checker.

    Returns True if path is under excluded file or directory, False otherwise.
    """
    (dir_exact, dir_globs), (file_exact, file_globs) = load_exclusions()

    if os.path.isdir(path):
        return (
            matches(path, dir_exact, dir_globs)
            or is_path_under_excluded_dir(path, dir_exact, dir_globs)
        )
    
    if os.path.isfile(path):
        return (
            matches(path, file_exact, file_globs)
            or is_path_under_excluded_dir(path, dir_exact, dir_globs)
        )

    return False

