import json
import socket
import getpass
import logging
import traceback

from shared import MultiUserRCPService

from .procedures import (
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
)

# Function registry
FUNCTIONS = {
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
    socket_path = f"/run/web-lgsm/{user}.sock"
    logging.basicConfig(level=1)

    MultiUserRCPService(None, handle_request, logging.getLogger("rpc_server")).serve(socket_path)

