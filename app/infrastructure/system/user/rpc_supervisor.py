import logging

from app.infrastructure.system.user.rpc_client import MultiUserRPCClient
from app.infrastructure.system.user.rpc_server_manager import MultiUserRPCServerManager

class MultiUserRPCSupervisor:
    """
    Ensures a user's RPC server is healthy before routing a call to it,
    restarting it first if necessary.
    """
    def __init__(self, logger=logging.getLogger(__name__), client=MultiUserRPCClient(), manager=MultiUserRPCServerManager()):
        self.logger = logger
        self.client = client
        self.manager = manager

    def call(self, func_name, *args, as_user=None, **kwargs):
        if as_user is not None and not self.manager.check(as_user):
            self.logger.debug(f"Health check failed for {as_user}, restarting")
            self.manager.restart(as_user)  # TODO: Catch failures here and re-init all sockets & acls

        return self.client.call(func_name, *args, as_user=as_user, **kwargs)
