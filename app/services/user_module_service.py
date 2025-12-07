import subprocess
import sys
import json
import os

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
                'sudo', '-u', as_user,
                f'PYTHONPATH=$PYTHONPATH:{self.module_dir}',
                sys.executable, '-m', 'shared.cli',
                json.dumps(data)
            ]

            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True,
            )

            return json.loads(result.stdout)

