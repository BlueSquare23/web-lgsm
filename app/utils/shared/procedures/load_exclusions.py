import os
import fnmatch
import yaml

def split_patterns(patterns):
    """
    Figures out which items are globs vs exact matches.
    """
    exact = set()
    globs = []

    for p in patterns:
        # if it contains glob chars, treat as glob
        if any(c in p for c in "*?[]"):
            globs.append(p)
        else:
            exact.add(p)

    return exact, globs


def load_exclusions():
    """
    Loads excluded dir and files from:
        /usr/local/share/web-lgsm_excluded.yml

    Returns two tupals containing two sets for exact dir and glob dir
    exclusions and exact file and glob file exclusions.
    """
    excluded = '/usr/local/share/web-lgsm_excluded.yml'
    if not os.path.isfile(excluded):
        return (set(), set()), (set(), set())

    with open(excluded, "r") as f:
        data = yaml.safe_load(f)

    dir_exact, dir_globs = split_patterns(data.get("exclude_dirs", []))
    file_exact, file_globs = split_patterns(data.get("exclude_files", []))

    return (dir_exact, dir_globs), (file_exact, file_globs)


