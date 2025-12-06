from .proc_info import ProcInfo

class ProcInfoService:
    """
    This singleton is used to access a shared dictionary of proc_info objects,
    allowing app to share info about the same processes between api and main
    views/routes.
    """
    # Holds ProcInfo objects.
    processes = dict()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ProcInfoService, cls).__new__(cls)
        return cls.instance

    def get_all_processes(self):
        """
        Get'em all
        """
        return ProcInfoService.processes


    def add_process(self, server_id, proc_info):
        """
        Adds a new proc_info object to shared dictionary.

        Args:
            server_id (int): Unique ID used to identify process. Often is ID of a
                             GameServer object, but not always.
            proc_info (ProcInfoVessel): Process object to be added to dictionary.
        """
        # Sets server_id for proc_info object automatically since we can.
        proc_info.server_id = server_id

        ProcInfoService.processes[server_id] = proc_info

        return proc_info

    def get_process(self, server_id, create=False):
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
        if server_id not in list(ProcInfoService.processes.keys()):
            if not create:
                return None

            self.add_process(server_id, proc_info=ProcInfo())

        return ProcInfoService.processes[server_id]

    def remove_process(self, server_id):
        """
        Removes any existing proc_info object from dictionary by server_id.

        Args:
            server_id (int): ID in database for GameServer object this process is
                             associated with.
        """
        if server_id in ProcInfoService.processes:
            del ProcInfoService.processes[server_id]

