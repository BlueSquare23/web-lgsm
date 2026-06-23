import os
import sys
import json
import logging

from threading import Thread

from flask import current_app

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
        self.game_server_repo = game_server_repo
        self.executor = executor
        self.module_dir = os.path.abspath(module_dir)
        self._threads: dict[str, Thread] = {}

    def _stop_thread(self, thread_name):
        """Stop a running thread by name if one exists, then remove it from tracking."""
        existing = self._threads.get(thread_name)

        if existing and existing.is_alive():
            self.logger.debug(f"Thread {thread_name} is alive, killing subprocess.")
            proc_info = self.executor.proc_info_repo.get(thread_name)

            if proc_info and proc_info.pid:
#                self.executor.run([PATHS['sudo'], '-n', '-u', user, PATHS['kill'], '-9', str(proc_info.pid)])
                os.kill(proc_info.pid, signal.SIGKILL)
            existing.join(timeout=5)

            if existing.is_alive():
                self.logger.warning(f"Thread {thread_name} did not stop within timeout.")

        self._threads.pop(thread_name, None)

    def launch(self):
        servers = self.game_server_repo.list()

        # Users set (auto unique)
        users = set()
        for server in servers:
            if server.install_type == 'remote':
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

            thread_name = f"rpc_server_thread_{user}"
            self.logger.debug(f"Starting Thread: {thread_name}")

            self._stop_thread(thread_name)

            daemon = Thread(
                target=self.executor.run,
                args=(cmd, None, thread_name, current_app.app_context()),
                daemon=True,
                name=thread_name,
            )
            daemon.start()
            self._threads[thread_name] = daemon
