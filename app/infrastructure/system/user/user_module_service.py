import os
import sys
import json
import logging
from datetime import datetime

from app.infrastructure.system.repositories.proc_info_repo import InMemProcInfoRepository

from app.infrastructure.system.command_executor.command_executor import CommandExecutor

class UserModuleService:
    """
    The user module service runs user module scripts. These module scripts are
    either imported and run (if no user specified), or run via sudo -u user to
    retrieve the json, allowing share user module scripts to be seamlessly run as
    multiple users.

    In/out via stdin/out json.
    """
    def __init__(self, module_dir='/opt/web-lgsm/utils', logger=logging.getLogger(__name__)):
        self.module_dir = os.path.abspath(module_dir)
        self.logger = logger

    def call(self, func_name, *args, as_user=None, **kwargs):
        """Call a function, optionally as another user"""

        # Same user import the code and run it.
        if as_user is None:
            sys.path.insert(0, self.module_dir)
            import importlib
            module = importlib.import_module('shared')
            func = getattr(module, func_name)
            return func(*args, **kwargs)

        # Otherwise execute via sudo -u via LocalCommandExecutor

        # Module script args & kwargs
        data = {
            'func': func_name,
            'args': args,
            'kwargs': kwargs
        }

        # Dump to json and encode as bytes
        stdin = json.dumps(data).encode("utf-8")
        self.logger.debug(stdin)

        # Subprocess cmd
        cmd = [
            'sudo', '-n', '-u', as_user,
            f'PYTHONPATH=$PYTHONPATH:{self.module_dir}',
            sys.executable, '-m', 'shared.cli',
        ]

        unique_time_str = datetime.now().strftime('%Y%m%d%H%M%S%f')
        cmd_id = 'user_module_service' + unique_time_str  # Keep proc_info id unique

        payload = {
            "cmd_id": cmd_id,
            "app_context": False,
            "timeout": False,
            "stdin": stdin
        }
        CommandExecutor().run(cmd, None, **payload)
        proc_info = InMemProcInfoRepository().get(cmd_id)

        if proc_info == None or proc_info.exit_status > 0:
            return {}

        # Undo post process on output for mod scripts.
        for index, line in enumerate(proc_info.stdout):
            proc_info.stdout[index] = line.replace("\r", "").replace("\n", "")

        module_out = "".join(proc_info.stdout)
        struct = json.loads(module_out)
        InMemProcInfoRepository().remove(cmd_id)  # Cleanup proc_info obj
        return struct

