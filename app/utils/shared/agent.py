import os
import json
import getpass
import logging
import traceback
import subprocess

from shared import MultiUserRCPService

from .procedures import (
    status,
    list_dir,
    is_dir,
    delete_file,
    rename_file,
    copy_tmp,
    cleanup_tmp,
    matches,
    is_excluded,
    traversal_safe,
    find_cfg_paths,
    edit_cron,
)

PLAYBOOKS = '/usr/local/share/web-lgsm'
with open(f"{PLAYBOOKS}/app_conf.json") as f:
    APP_USER = json.load(f)["APP_USER"]

# Function registry
FUNCTIONS = {
    "status": status,
    "list_dir": list_dir,
    "is_dir": is_dir,
    "delete_file": delete_file,
    "rename_file": rename_file,
    "copy_tmp": copy_tmp,
    "cleanup_tmp": cleanup_tmp,
    "matches": matches,
    "is_excluded": is_excluded,
    "traversal_safe": traversal_safe,
    "find_cfg_paths": find_cfg_paths,
    "edit_cron": edit_cron,
}

# Request handler
def handle_request(payload):
    try:
        func_name = payload.get("func")
        args = payload.get("args", [])
        kwargs = payload.get("kwargs", {})

        if func_name not in FUNCTIONS:
            return {"ok": False, "error": f"unknown function: {func_name}"}

        fn = FUNCTIONS[func_name]
        result = fn(*args, **kwargs)

        return {"ok": True, "result": result}

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "trace": traceback.format_exc(),
        }

# Entry point
if __name__ == "__main__":
    user = getpass.getuser()
    runtime_dir = os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}"
    socket_path = os.path.join(runtime_dir, "web-lgsm-agent.sock")

    # Let only the app user traverse into our own private runtime dir.
    subprocess.run(["/usr/bin/setfacl", "-m", f"u:{APP_USER}:x", runtime_dir], check=True)

    logging.basicConfig(level=1)

    MultiUserRCPService(None, handle_request, APP_USER, logging.getLogger("rpc_server")).serve(socket_path)

