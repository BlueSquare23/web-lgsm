import os
import sys
import pwd
import json
import logging

from app.utils.paths import PATHS

from app.infrastructure.system.user.rpc_client import MultiUserRPCClient
from app.infrastructure.system.command_executor.command_executor import CommandExecutor
from app.infrastructure.system.repositories.proc_info_repo import InMemProcInfoRepository
from app.infrastructure.persistence.repositories.game_server_repo import SqlAlchemyGameServerRepository

class MultiUserRPCServerManager:
    """
    Responsible for starting and managing the state of (aka kicking) Multi User
    RCP Servers running as each game server system user.

    Start per user rpc servers via systemd service at app startup. Restarts them on demand.
    """

    def __init__(self, logger=logging.getLogger(__name__), game_server_repo=SqlAlchemyGameServerRepository(), executor=CommandExecutor(), client=MultiUserRPCClient(), socket_dir="/run/web-lgsm", module_dir='/opt/web-lgsm/utils'):
        self.logger = logger
        self.game_server_repo = game_server_repo
        self.executor = executor
        self.client = client
        self.socket_dir = os.path.abspath(socket_dir)
        self.module_dir = os.path.abspath(module_dir)

    def _manage(self, user, verb):
        """
        General purpose manager for stop, start, and restart RPC systemd
        services running as users.
        """
        allowed_verbs = ['start', 'stop', 'restart']
        assert verb in allowed_verbs

        self.logger.debug(f"{verb}ing RPC server for: {user}")
        pwent = pwd.getpwnam(user)

        cmd_id = f'{verb}_rpc_server_{user}'
        cmd = [
            PATHS['sudo'],
            '-n', '-u', user,
            f'XDG_RUNTIME_DIR=/run/user/{pwent.pw_uid}',
            PATHS['systemctl'],
            '--user', verb, 'web-lgsm-agent'
        ]
        return self.executor.run(cmd, None, cmd_id)

    def stop(self, user):
        return self._manage(user, 'stop')

    def start(self, user):
        return self._manage(user, 'start')

    def restart(self, user):
        return self._manage(user, 'restart')

    def check(self, user):
        """
        Uses rpc client to preform status / health checks bc its faster than
        jobbing out to systemctl.
        """
        status = self.client.call('status', as_user=user)
        if status['success']:
            return status['success']

        return False
        
    def launch(self):
        """
        Ensures RPC servers for all users are started.
        """
        servers = self.game_server_repo.list()

        # Users set (auto unique)
        users = set()
        for server in servers:
            if server.install_type == 'remote' or server.install_type == 'docker':
                continue
            users.add(server.username)

        self.logger.debug(users)

        for user in users:
            if not self.check(user):
                self.start(user)

