import re
import json
import time
import threading
import logging

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

    def __init__(self, game_server_repository=SqlAlchemyGameServerRepository(), logger=logging.getLogger(__name__)):
        self.game_server_repository=game_server_repository
        self.logger = logger

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
        cmd = GameServerInstallManager.CONNECTOR_CMD + ["--cancel", str(pid)]

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

                server = self.game_server_repository.get(server_id)

                # Check game server exists.
                if server:
                    running_install_threads[server_id] = server.install_name

        return running_install_threads

    def clear_proc_info_post_install(self, server_id, app_context):
        """
        Clears the stdout & stderr buffers for proc_info after install finishes.
        Does so by checking running install threads, if thread for ID is gone from
        running list and game server install marked finished, clear buffers.
    
        Args:
            server_id (str): UUID for game server.
            app_context (AppContext): Optional Current app context needed for
                                      logging in a thread.
        """

        # App context needed for logging in threads.
        if app_context:
            app_context.push()

        max_lifetime = 3600  # 1 Hour TTL
        runtime = 0

        # Little buffer to make sure install daemon thread starts first.
        time.sleep(5)

#TODO: Sort out logger call, I need a standardized way to do them. I don't like this passing in current app to infra layer.
        self.logger.info("<CLEAR DAEMON> - Starting clear thread")

        while runtime < max_lifetime:
            all_installs = get_running_installs()

            # Aka install finished or died.
            if server_id not in all_installs:
                server = self.game_server_repository.get(server_id)
    
                # Rare edge case if server deleted before thread dies.
                if server == None:
                    return

                # If install thread not running anymore and install marked
                # finished, clear out the old proc_info object.
                if server.install_finished and not server.install_failed:
                    self.logger.info("<CLEAR DAEMON> - Thread Cleared!")
                    InMemProcInfoRepository.remove(server_id)
                    return

            time.sleep(5)
            runtime += 5

