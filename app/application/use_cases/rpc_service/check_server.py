class CheckRPCServer:

    def __init__(self, rpc_server_manager):
        self.rpc_server_manager = rpc_server_manager

    def execute(self, user):
        return self.rpc_server_manager.check(user)

