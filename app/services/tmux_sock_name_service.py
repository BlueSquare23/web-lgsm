import os
import getpass

from app import cache
from app.models import GameServer

from .user_module_service import UserModuleService
from .file_manager_service.file_manager_service import FileManagerService

class TmuxSocketNameService:

    def del_socket_name_cache(self, server_id):
        """
        Deletes cache of sock file names for GameServers. Used by setting page
        option. Useful for when game server has been re-installed to get status
        indicators working again.
        """
        cache_key = server_id + 'socket_name'
        cache.delete(cache_key)
    
    def get_tmux_socket_name(self, server):
        """
        Get's the tmux socket file name for a given game server. Will cache
        tmux socket names to save on number of ssh / system calls.
    
        Args:
            server (GameServer): Game Server to get tmux socket name for.
    
        Returns:
            str: Returns the socket name for game server. None if can't get socket
                 name.
        """
        assert isinstance(server, GameServer), "server is not an instance of GameServer"

        gs_id_file_path = os.path.join(
            server.install_path, f"lgsm/data/{server.script_name}.uid"
        )
    
        cache_key = server.id + 'socket_name'
        socket_file_name = cache.get(cache_key)

        if socket_file_name == None:  # Aka cache empty
            file_manager = FileManagerService(server)
            gs_id = file_manager.read_file(gs_id_file_path)
            if gs_id == None:
                return None

            socket_file_name = server.script_name + "-" + gs_id.rstrip()
            cache.set(cache_key, socket_file_name, timeout=1800)

        return socket_file_name


