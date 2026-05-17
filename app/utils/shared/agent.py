import os
import json
import socket
import traceback
import logging

from shared import MultiUserRCPService

from shared import (
    read_file,
    list_dir,
    delete_file,
    rename_file,
    write_file,
    matches,
    is_excluded,
    traversal_safe,
)

logger = logging.getLogger("rpc_sockd_server")


# Function registry (important)
FUNCTIONS = {
    "read_file": read_file,
    "list_dir": list_dir,
    "delete_file": delete_file,
    "rename_file": rename_file,
    "write_file": write_file,
    "matches": matches,
    "is_excluded": is_excluded,
    "traversal_safe": traversal_safe,
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
    user = os.getlogin()
    socket_path = f"/run/web-lgsm/{user}.sock"
    logging.basicConfig(level=3)

    MultiUserRCPService(None, handle_request, logging.getLogger("rpc_sockd_server")).serve(socket_path)

