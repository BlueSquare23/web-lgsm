class StartRPCServers:

    def __init__(self, rpc_server_manager):
        self.rpc_server_manager = rpc_server_manager

    def execute(self):
        return self.rpc_server_manager.launch()

