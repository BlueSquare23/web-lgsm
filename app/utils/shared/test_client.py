import os
import logging

from shared import MultiUserRCPService

logging.basicConfig(level=3)

user = os.getlogin()
socket_path = f"/run/web-lgsm/{user}.sock"
logging.getLogger("rpc_sockd_client")

#resp = MultiUserRCPService(None, None, logging.getLogger("rpc_sockd_client")).send('{"func": "list_dir", "args": ["/home/blue"]}', socket_path)
resp = MultiUserRCPService(None, None, logging.getLogger("rpc_sockd_client")).send('{"func": "fart", "args": ["/home/blue"]}', socket_path)
print(resp)
