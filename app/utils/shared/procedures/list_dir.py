import os
import grp
import pwd
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
            info = entry.stat(follow_symlinks=False)

            item_type = 'dir' if stat.S_ISDIR(info.st_mode) else 'file'

            if not show_hidden and entry.name.startswith("."):
                continue

            if item_type == 'dir':
                if matches(entry.path, dir_exact, dir_globs):
                    continue
            else:
                if matches(entry.name, file_exact, file_globs):
                    continue

            # Get readable string (e.g., '-rw-r--r--')
            perms = stat.filemode(info.st_mode)

            # Get uids/gids
            uid = info.st_uid
            gid = info.st_gid

            # Convert IDs to human-readable names
            user = pwd.getpwuid(uid).pw_name
            group = grp.getgrgid(gid).gr_name
            
            files.append({
                "name": entry.name,
                "path": entry.path,
                "type": item_type,
                "user": user,
                "group": group,
                "perms": perms,
                "size": info.st_size
            })

    return files

