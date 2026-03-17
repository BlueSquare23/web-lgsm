import re
import json
import threading

from app.infrastructure.persistence.repositories.game_server_repo import SqlAlchemyGameServerRepository
from app.infrastructure.system.repositories.proc_info_repo import InMemProcInfoRepository
from app.infrastructure.system.command_executor.command_executor import CommandExecutor

from app.utils.paths import PATHS

class GameServerInstallManager:
    """
    System interface for managing concrete parts of game server installs.
    """
    CONNECTOR_CMD = [
        PATHS["sudo"],
        "-n",
        "/opt/web-lgsm/bin/python",
        PATHS["ansible_connector"],
    ]

    def list(self):
        """
        Get list of install-able game servers. Turns data in games_servers.json
        into list for install route.

        Returns:
            dict: Dictionary mapping short server names to long server names.
        """

        import os
        print(os.getcwd())

        with open("json/game_servers.json", "r") as file:
            json_data = json.load(file)
    
        return {
            key: (value1, value2)
            for key, value1, value2 in zip(
                json_data["servers"],
                json_data["server_names"],
                json_data["app_imgs"]
            )
        }


    def cancel(self, pid):
        """ 
        Calls the ansible playbook connector to kill running installs upon request.

        Args:
            pid (int): Process ID or running install to cancel.

        Returns:
            bool: True if install canceled successfully, False otherwise.
        """

        # NOTE: For the --cancel option on the ansible connector script we pass in
        # the pid of the running install, instead of a game server's ID.
        cmd = GameServerManager.CONNECTOR_CMD + ["--cancel", str(pid)]

        cmd_id = 'cancel_install'
        CommandExecutor().run(cmd, None, cmd_id)
        proc_info = InMemProcInfoRepository().get(cmd_id)

        if proc_info == None:
            return False

        if proc_info.exit_status > 0:
            return False

        return True

    def list_running(self):
        """
        Gets list of running install thread names, if any are currently running.
    
        Returns:
            dict: Mapping of observed running threads for game server IDs to game
                  server names.
        """
        threads = threading.enumerate()
        # Get all active threads.
        running_install_threads = dict()
    
        for thread in threads:
            if thread.is_alive() and thread.name.startswith("web_lgsm_install_"):
                server_id = thread.name.replace("web_lgsm_install_", "")
                if not server_id:
                    continue
                server = SqlAlchemyGameServerRepository.get(server_id)
    
                # Check game server exists.
                if server:
                    running_install_threads[server_id] = server.install_name
    
        return running_install_threads

