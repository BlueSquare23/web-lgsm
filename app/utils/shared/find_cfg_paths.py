import os

def find_cfg_paths(search_path, names):
    """
    Finds a list of all valid cfg files for a given game server.

    Args:
        search_path (str): Game server to find cfg files for.
        names (list): List of valid cfg file names. 

    Returns:
        cfg_paths (list): List of found valid config files.
    """
    cfg_paths = []

    # Find all cfgs under install_path using os.walk.
    for root, dirs, files in os.walk(search_path):
        # Ignore default cfgs.
        if "config-default" in root:
            continue
        for file in files:
            if file in names:
                cfg_paths.append(os.path.join(root, file))

    return cfg_paths
