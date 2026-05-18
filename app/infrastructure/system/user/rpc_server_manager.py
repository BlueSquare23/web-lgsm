import os
import sys
import json
import logging

from threading import Thread

from flask import current_app  # NOT CLEAN but for rn I don't care, pass in via dep inversion somehow in future.

from app.utils.paths import PATHS

from app.infrastructure.persistence.repositories.game_server_repo import SqlAlchemyGameServerRepository
from app.infrastructure.system.repositories.proc_info_repo import InMemProcInfoRepository
from app.infrastructure.system.command_executor.command_executor import CommandExecutor

class MultiUserRPCServerManager:
    """
    Responsible for starting and managing the state of (aka kicking) Multi User
    RCP Servers running as each game server system user.

    Start per user rpc servers in threads at app startup. Restarts them on demand.
    """

    def __init__(self, logger=logging.getLogger(__name__), socket_dir="/run/web-lgsm", game_server_repo=SqlAlchemyGameServerRepository(), executor=CommandExecutor(), module_dir='/opt/web-lgsm/utils'):
        self.logger = logger
        self.socket_dir = socket_dir
        self.game_server_repo =  game_server_repo
        self.executor = executor
        self.module_dir = os.path.abspath(module_dir)

    def launch(self):
        servers = self.game_server_repo.list()

        # Users set (auto unique)
        users = set()
        for server in servers:
            if server.install_type == 'remote':  # For now skip remote installs for rpc service, although some day...
                continue
            users.add(server.username)

        self.logger.debug(users)

        for user in users:
            cmd = [
                PATHS["sudo"],
                '-n', '-u', user,
                f'PYTHONPATH=$PYTHONPATH:{self.module_dir}',
                sys.executable, '-m', 'shared.agent'
            ]

            thread_name = f"rpc_server_thread_{server.install_name}"
            self.logger.debug(f"Starting Thread: {thread_name}")

            daemon = Thread(
                target=self.executor.run,
                args=(cmd, None, thread_name, current_app.app_context()),
                daemon=True,
                name=thread_name,
            )
            daemon.start()


