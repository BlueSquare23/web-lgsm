import os
import getpass

from app import cache
from app.models import GameServer

from .user_module_service import UserModuleService
from .file_manager_service.file_manager_service import FileManagerService

#{"7b2dddb1-58d0-4c76-b81a-c23c820264a8": "bf1942server-1f93f3de"}


class TmuxSocketNameService:

    # TODO: Probably can just put this in the current_app var or something. Idk fine for now.
    USER = getpass.getuser()

    def __init__(self):
        self.executor = UserModuleService()

    def purge_tmux_socket_cache():
        """
        Deletes local cache of sock file names for installs. Used by setting page
        option. Useful for when game server has been re-installed to get status
        indicators working again.
        """
        socket_file_name_cache = os.path.join(CWD, "json/tmux_socket_name_cache.json")
        if os.path.exists(socket_file_name_cache):
            os.remove(socket_file_name_cache)
    
    
    def get_tmux_socket_name_docker(server, gs_id_file_path):
        """
        Gets tmux socket name for docker type installs by running commands through
        CommandExecService.run_command().
    
        Args:
            server (GameServer): Game Server to get tmux socket name for.
            gs_id_file_path (str): Path to gs_id file for game server.
    
        Returns:
            str: Returns the socket name for game server. None if can't get
                 socket name.
        """
        from app.services import ProcInfoService, CommandExecService
        cmd = docker_cmd_build(server) + [PATHS["cat"], gs_id_file_path]
    
        cmd_id = "get_tmux_socket_name_docker"
    
        CommandExecService(ConfigManager()).run_command(cmd, None, cmd_id)
        proc_info = ProcInfoService().get_process(cmd_id)
    
        if proc_info.exit_status > 0:
            current_app.logger.info(proc_info)
            return None
    
        gs_id = proc_info.stdout[0].strip()
    
        if len(gs_id) == 0:
            return None
    
        return server.script_name + "-" + gs_id
    
    
    def get_tmux_socket_name_over_ssh(server, gs_id_file_path):
        """
        Uses SSH to get tmux socket name for remote and non-same user installs.
    
        Args:
            server (GameServer): Game Server to get tmux socket name for.
            gs_id_file_path (str): Path to gs_id file for game server.
    
        Returns:
            str: Returns the socket name for game server. None if can't get
                 socket name.
        """
        from app.services import ProcInfoService, CommandExecService
        cmd = [PATHS["cat"], gs_id_file_path]
    
        success = CommandExecService(ConfigManager()).run_command(cmd, server, server.id)
        proc_info = ProcInfoService().get_process(server.id)
        if proc_info == None:
            return None
    
        # If the ssh connection itself fails return None.
        if not success:
            current_app.logger.info(proc_info)
            return None
    
        if proc_info.exit_status > 0:
            current_app.logger.info(proc_info)
            return None
    
        gs_id = proc_info.stdout[0].strip()
    
        if len(gs_id) == 0:
            return None
    
        return server.script_name + "-" + gs_id
    
    
    def update_tmux_socket_name_cache(server_id, socket_name, delete=False):
        """
        Writes to tmux socket name cache with fresh data.
    
        Args:
            server_id (int): ID of Game Server to get tmux socket name for.
            delete (bool): If delete specified, given entry will be removed.
    
        Returns:
            None
        """
        cache_file = os.path.join(CWD, "json/tmux_socket_name_cache.json")
        cache_data = dict()
        current_app.logger.debug(log_wrap("Updating cache for server_id:", server_id))
    
        if os.path.exists(cache_file):
            with open(cache_file, "r") as file:
                cache_data = json.load(file)
    
        if delete:
            # Json.dump casts int to str. So need to re-cast to str on delete.
            server_id = str(server_id)
            if server_id in cache_data:
                del cache_data[server_id]
        else:
            cache_data[server_id] = socket_name
    
        with open(cache_file, "w") as file:
            json.dump(cache_data, file)
    
    
    def get_tmux_socket_name_from_cache(server, gs_id_file_path):
        """
        Get's the tmux socket name for remote, docker, and non-same user installs
        from the cache. If there is no cache file get socket for server and create
        cache. If the cache file is older than a week get socket name and update
        cache. Otherwise just pull the socket name value from the json cache.
    
        Args:
            server (GameServer): Game Server to get tmux socket name for.
            gs_id_file_path (str): Path to gs_id file for game server.
    
        Returns:
            str: Returns the socket name for game server. None if cant get
                 one.
        """

        cache_file = os.path.join(CWD, "json/tmux_socket_name_cache.json")
    
        if not os.path.exists(cache_file):
            if server.install_type == "docker":
                socket_name = get_tmux_socket_name_docker(server, gs_id_file_path)
            else:
                socket_name = get_tmux_socket_name_over_ssh(server, gs_id_file_path)
            update_tmux_socket_name_cache(server.id, socket_name)
            return socket_name
    
        # Check if cache has expired.
        cache_mtime = os.path.getmtime(cache_file)
    
        # Convert the mtime to a datetime object.
        cache_time = datetime.fromtimestamp(cache_mtime)
    
        current_time = datetime.now()
        one_week_ago = current_time - timedelta(weeks=1)
    
        # Time comparisons always confuse me. With Epoch time, bigger number ==
        # more recent. Aka if the epoch time of one week ago is larger than the
        # epoch timestamp of cache file than the cache must be older than a week.
        if cache_time < one_week_ago:
            if server.install_type == "docker":
                socket_name = get_tmux_socket_name_docker(server, gs_id_file_path)
            else:
                socket_name = get_tmux_socket_name_over_ssh(server, gs_id_file_path)
    
            update_tmux_socket_name_cache(server.id, socket_name)
            return socket_name
    
        with open(cache_file, "r") as file:
            cache_data = json.load(file)
    
        if str(server.id) not in cache_data:
            if server.install_type == "docker":
                socket_name = get_tmux_socket_name_docker(server, gs_id_file_path)
            else:
                socket_name = get_tmux_socket_name_over_ssh(server, gs_id_file_path)
    
            update_tmux_socket_name_cache(server.id, socket_name)
            return socket_name
    
        socket_name = cache_data[str(server.id)]
        return socket_name
    
    def get_tmux_socket_name(self, server):
        """
        Get's the tmux socket file name for a given game server. Will call
        get_tmux_socket_name_from_cache() for remote, docker, & non-same user
        installs, otherwise will just read the gs_id value from the local file
        system to build the socket name.
    
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
    
        socket_file_name = cache.get(server.id + 'socket_name')
        if socket_file_name == None:  # Aka cache empty
            file_manager = FileManagerService(server)
            gs_id = file_manager.read_file(gs_id_file_path)

        return server.script_name + "-" + gs_id.rstrip()


