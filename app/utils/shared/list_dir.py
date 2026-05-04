import os
import stat
from .matches import matches
from .load_exclusions import load_exclusions
from .is_excluded import is_excluded

def list_dir(directory, show_hidden=True):
    """
    Lists directories, ignores excluded file/dir names/globs.
    """
    files = []

    if not os.path.isdir(directory):
        return files

    if is_excluded(directory):
        return files

    (dir_exact, dir_globs), (file_exact, file_globs) = load_exclusions()

    with os.scandir(directory) as entries:
        for entry in entries:
            item_type = 'dir' if entry.is_dir(follow_symlinks=False) else 'file'

            if not show_hidden and entry.name.startswith("."):
                continue

            if item_type == 'dir':
                if matches(entry.path, dir_exact, dir_globs):
                    continue
            else:
                if matches(entry.name, file_exact, file_globs):
                    continue

            info = entry.stat()

            # Get raw octal permissions (e.g., 0o644)
            perms_octal = oct(info.st_mode & 0o777)
            
            # Get readable string (e.g., '-rw-r--r--')
            perms = stat.filemode(info.st_mode)
            
            files.append({
                "name": entry.name,
                "path": entry.path,
                "type": item_type,
                "perms": perms
            })

    return files

