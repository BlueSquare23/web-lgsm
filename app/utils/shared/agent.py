import os
import json
import socket
import traceback
import logging

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

logger = logging.getLogger("user-agent")

SOCKET_PATH = None


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


# Server loop
def serve(socket_path):
    global SOCKET_PATH
    SOCKET_PATH = socket_path

    if os.path.exists(socket_path):
        os.remove(socket_path)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(socket_path)

    # 660 so only owner/group can access
    os.chmod(socket_path, 0o660)

    sock.listen(128)

    logger.info(f"UserAgent listening on {socket_path}")

    while True:
        conn, _ = sock.accept()

        try:
            data = conn.recv(65536)
            if not data:
                continue

            payload = json.loads(data.decode("utf-8"))
            response = handle_request(payload)

            conn.sendall(json.dumps(response).encode("utf-8"))

        except Exception as e:
            err = {
                "ok": False,
                "error": "agent crash",
                "detail": str(e),
            }
            conn.sendall(json.dumps(err).encode("utf-8"))

        finally:
            conn.close()


# Entry point
if __name__ == "__main__":
    import sys

    user = os.getlogin()
    socket_path = f"/run/web-lgsm/{user}.sock"

    serve(socket_path)
