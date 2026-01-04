from flask import current_app
from app.utils.paths import PATHS
from app.utils.helpers import log_wrap

from app.config import ConfigManager

from .tmux_socket_name_cache import TmuxSocketNameCache
from .proc_info.proc_info_registry import ProcInfoRegistry
from .command_exec.command_executor import CommandExecutor

class ServerPowerState:

    def get_status(self, server):
        """
        Get's the game server status (on/off) for a specific game server. For
        install_type local same user, does so by running tmux cmd locally. For
        install_type remote and local not same user, fetches status by running tmux
        cmd over SSH. For install_type docker, uses docker cmd to fetch status.
    
        Args:
            server (GameServer): Game server object to check status of.
        Returns:
            bool|None: True if game server is active, False if inactive, None if
                       indeterminate.
        """
        socket = TmuxSocketNameCache().get_tmux_socket_name(server)
        if socket == None:
            return None
    
        cmd = [PATHS["tmux"], "-L", socket, "list-session"]
    
        cmd_id = "get_server_status:" + server.install_name
    
        CommandExecutor(ConfigManager()).run_command(cmd, server, cmd_id)
    
        proc_info = ProcInfoRegistry().get_process(cmd_id)
        current_app.logger.info(log_wrap("proc_info", proc_info))
    
        if proc_info == None:
            return None
    
        if proc_info.exit_status > 0:
            return False
    
        return True
    
