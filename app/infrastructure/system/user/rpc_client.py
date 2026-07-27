import os
import sys
import json
import logging

class MultiUserRPCClient:
    """
    The user module service runs user module scripts. These module scripts are
    either imported and run (if no user specified), or run via sudo -u user to
    retrieve the json, allowing share user module scripts to be seamlessly run as
    multiple users.

    In/out via stdin/out json.
    """
    def __init__(self, module_dir='/opt/web-lgsm/utils', logger=logging.getLogger(__name__), socket_dir="/run/web-lgsm"):
        self.module_dir = os.path.abspath(module_dir)
        self.logger = logger
        self.socket_dir = socket_dir

    def call(self, func_name, *args, as_user=None, **kwargs):
        """Call a function, optionally as another user"""

        # Add module dir to path
        sys.path.insert(0, self.module_dir)
        import importlib
        module = importlib.import_module('shared.procedures')

        self.logger.debug(args)

        # Same user import the code and run it.
        if as_user is None:
            func = getattr(module, func_name)
            return func(*args, **kwargs)

        from shared import MultiUserRCPService

        socket_path = f"{self.socket_dir}/{as_user}.sock"

        payload = json.dumps({
            "func": func_name,
            "args": args,
            "kwargs": kwargs,
        })

        client = MultiUserRCPService(None, None, logging.getLogger("rpc_client"))
        try:
            resp = client.send(payload, socket_path)
            return resp
        except Exception as e:
            return {"status":"failure", "reason": f"RCP client failed with: {e}"}


