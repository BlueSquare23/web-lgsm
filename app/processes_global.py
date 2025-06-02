# This file holds the shared global processes dict and associated function.
# This dictionary is used by both views.py and api.py as a module-level (aka
# poor-mans) singleton. Aka gives us access to same dictionary of
# ProcInfoVessel objects between api and views routes.

from .proc_info_vessel import ProcInfoVessel

# Holds ProcInfoVessel objects.
processes = dict()


def get_all_processes():
    """
    Get'em all
    """
    return processes


def add_process(server_id, proc_info):
    """
    Adds a new proc_info object to shared dictionary.

    Args:
        server_id (int): Unique ID used to identify process. Often is ID of a
                         GameServer object, but not always.
        proc_info (ProcInfoVessel): Process object to be added to dictionary.
    """
    # Sets server_id for proc_info object automatically since we can.
    proc_info.server_id = server_id

    processes[server_id] = proc_info

    return proc_info


def get_process(server_id, create=False):
    """
    Fetches existing proc_info object from dictionary by server_id.

    Args:
        server_id (int): ID in database for GameServer object this process is
                         associated with.
        create (bool): Optional Create new process if none found.                         

    Returns:
        proc_info (ProcInfoVessel): Returns proc_info object in dictionary,
        else returns None.
    """
    if server_id not in list(processes.keys()):
        if not create:
            return None

        add_process(server_id, proc_info=ProcInfoVessel())

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
