import subprocess
import sys
import json
import os

from flask import current_app

from app.config import ConfigManager
from .command_exec_service.command_exec_service import CommandExecService
from .proc_info_service.proc_info_service import ProcInfoService

class UserModuleService:
    """
    The user module service runs user module scripts. These module scripts are
    either imported and run (if no user specified), or run via sudo -u user to
    retrieve the json, allowing share user module scripts to be seamlessly run as
    multiple users.

    In/out via stdin/out json.
    """
    def __init__(self, module_dir):
        self.module_dir = os.path.abspath(module_dir)

    def call(self, func_name, *args, as_user=None, **kwargs):
        """Call a function, optionally as another user"""

        if as_user is None:
            sys.path.insert(0, self.module_dir)
            import importlib
            module = importlib.import_module('shared')
            func = getattr(module, func_name)
            return func(*args, **kwargs)
        else:
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

            cmd_id = 'user_module_service'
            CommandExecService(ConfigManager()).run_command(cmd, None, cmd_id)
            proc_info = ProcInfoService().get_process(cmd_id)

            if proc_info == None or proc_info.exit_status > 0:
                return {}

            module_out = "\n".join(proc_info.stdout)
            current_app.logger.info(json.loads(module_out))
            return json.loads(module_out)

