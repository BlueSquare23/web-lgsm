class FindGameServerCfgPaths:

    def __init__(self, cfg_manager):
        self.cfg_manager = cfg_manager

    def execute(self, server):
        """
        Find's game server cfg file paths
        """
        return self.cfg_manager.find_cfg_paths(server)
