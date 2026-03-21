import subprocess
import sys
import json
import os
from datetime import datetime

# TODO: REMOVE THIS --v
from flask import current_app

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
    def __init__(self, module_dir='/opt/web-lgsm/utils'):
        self.module_dir = os.path.abspath(module_dir)

    def call(self, func_name, *args, as_user=None, **kwargs):
        """Call a function, optionally as another user"""

        if as_user is None:
            sys.path.insert(0, self.module_dir)
            import importlib
            module = importlib.import_module('shared')
            func = getattr(module, func_name)
            return func(*args, **kwargs)

        # Execute via sudo, importing the same module
        data = {
            'func': func_name,
            'args': args,
            'kwargs': kwargs
        }

        cmd = [
            'sudo', '-n', '-u', as_user,
            f'PYTHONPATH=$PYTHONPATH:{self.module_dir}',
            sys.executable, '-m', 'shared.cli',
            json.dumps(data)
        ]

        unique_time_str = datetime.now().strftime('%Y%m%d%H%M%S%f')
        cmd_id = 'user_module_service' + unique_time_str  # Keep proc_info id unique
        CommandExecutor().run(cmd, None, cmd_id)
        proc_info = InMemProcInfoRepository().get(cmd_id)

        if proc_info == None or proc_info.exit_status > 0:
            return {}

        try:
            module_out = "\n".join(proc_info.stdout)
            struct = json.loads(module_out)
            InMemProcInfoRepository().remove(cmd_id)  # Cleanup proc_info obj
            return struct
        except:
            return module_out
            
