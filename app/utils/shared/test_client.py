import os
import logging

from shared.rpc_sockd_client import MultiUserRCPSocketDClient

logging.basicConfig(level=3)

user = os.getlogin()
socket_path = f"/run/web-lgsm/{user}.sock"

resp = MultiUserRCPSocketDClient().send('{"func": "list_dir", "args": ["/home/blue"]}', socket_path)
print(resp)
