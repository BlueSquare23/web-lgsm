# This file holds the shared global processes dict and associated function.
# This dictionary is used by both views.py and api.py as a module-level (aka
# poor-mans) singleton. Aka gives us access to same dictionary of
# ProcInfoVessel objects between api and views routes.

from .proc_info_vessel import ProcInfoVessel

# Singletonawopaguz.
processes = {}  # Holds ProcInfoVessel objects.

def get_all_processes():
    return processes

def add_process(server_id, proc_info=ProcInfoVessel()):
    """
    Adds a new proc_info object to shared dictionary.

    Args:
        server_id (int): ID in database for GameServer object this process is
                         associated with.
        proc_info (ProcInfoVessel): Process object to be added to dictionary.
    """
    # Sets server_id for proc_info object automatically since we can.
    proc_info.server_id = server_id

    processes[server_id] = proc_info

    return proc_info


def get_process(server_id):
    """
    Fetches existing proc_info object from dictionary by server_id.

    Args:
        server_id (int): ID in database for GameServer object this process is
                         associated with.

    Returns:
        proc_info (ProcInfoVessel): Returns proc_info object in dictionary,
                                    else returns None.
    """
    return processes[server_id]


def remove_process(server_id):
    """
    Removes any existing proc_info object from dictionary by server_id.

    Args:
        server_id (int): ID in database for GameServer object this process is
                         associated with.
    """
    if server_id in processes:
        del processes[server_id]
