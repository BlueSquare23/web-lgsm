import re
import getpass
import logging

from app.infrastructure.system.repositories.proc_info_repo import InMemProcInfoRepository
from app.infrastructure.system.command_executor.command_executor import CommandExecutor

from app.utils.paths import PATHS

from app.utils.helpers import log_wrap

from .tmux_socket_name_cache import TmuxSocketNameCache

class GameServerManager:
    """
    System interface for managing concrete parts of game servers.
    """
    CONNECTOR_CMD = [
        PATHS["sudo"],
        "-n",
        "/opt/web-lgsm/bin/python",
        PATHS["ansible_connector"],
    ]
    USER = getpass.getuser()

    def __init__(self, logger=logging.getLogger(__name__)):
        self.logger = logger

    def _normalize_path(path):
        """
        Little helper function used to normalize supplied path in order to
        check if two path str's are equivalent. Used to ensure NOT deleting home dir by
        any other name.
    
        Args:
            path (str): Path to clear up
    
        """
        # Remove extra slashes.
        path = re.sub(r"/{2,}", "/", path)

        # Remove trailing slash unless it's the root path "/".
        if path != "/" and path.endswith("/"):
            path = path[:-1]

        return path


    # TODO: Replace failure flash cases below with custom exceptions to
    # communicate more information to the user! Basically, long ago before
    # refactors this used to live in route code and exceptions were made known
    # to the user directly. 
    #
    # Now we've abstracted this, so exceptions need explicitly bubbled up.
    # Still haven't totally figured out how I'm handling exceptions yet tbh.
    def delete(self, server, delete_user):
        """
        Does the actual deletions for the /delete route.

        Args:
            server (GameServer): Game server to delete.

        Returns:
            Bool: True if deletion was successful, False if something went wrong.
        """

        if server.install_type == "local":
            if server.username == GameServerManager.USER:
                if self._normalize_path(f"/home/{GameServerManager.USER}") == self._normalize_path(server.install_path):
                    flash("Will not delete users home directories!", category="error")
                    return False

                if self._normalize_path(CWD) == self._normalize_path(server.install_path):
#                    flash(
#                        "Will not delete web-lgsm base installation directory!",
#                        category="error",
#                    )
                    return False

                if os.path.isdir(server.install_path):
                    shutil.rmtree(server.install_path)

            if delete_user and server.username != GameServerManager.USER:
                cmd = GameServerManager.CONNECTOR_CMD + ["--delete", str(server.id)]
                CommandExecutor().run(cmd)

        if server.install_type == "remote":
#            if delete_user:
#                flash(
#                    f"Warning: Cannot delete game server users for remote installs. Only removing files!"
#                )

            # Check to ensure is not a home directory before delete. Just some
            # idiot proofing, myself being the chief idiot.
            if self._normalize_path(f"/home/{server.username}") == self._normalize_path(
                server.install_path
            ):
#                flash("Will not delete remote users home directories!", category="error")
                return False

            cmd = [PATHS["rm"], "-rf", server.install_path]

            success = CommandExecutor().run(cmd, server, server.id)
            proc_info = InMemProcInfoRepository().get(server.id)

            # If the ssh connection itself fails return False.
            if not success or proc_info == None:
                self.logger.info(log_wrap("proc_info", proc_info))
#                flash("Problem connecting to remote host!", category="error")
                return False

            if proc_info.exit_status > 0:
                self.logger.info(proc_info)
#                flash("Delete command failed! Check logs for more info.", category="error")
                return False

        return True


    def get_power_state(self, server):
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
    
        CommandExecutor().run(cmd, server, cmd_id)
    
        proc_info = InMemProcInfoRepository().get(cmd_id)
        self.logger.info(log_wrap("proc_info", proc_info))
    
        if proc_info == None:
            return None
    
        if proc_info.exit_status > 0:
            return False
    
        return True

