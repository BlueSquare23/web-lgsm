import fnmatch

def matches(path, exact_set, glob_list):
    """
    Compares str path to items in sets.
    """
    # O(1)
    if path in exact_set:
        return True

    # O(n), but usually small
    return any(fnmatch.fnmatch(path, g) for g in glob_list)

