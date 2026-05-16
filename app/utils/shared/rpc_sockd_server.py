import os
import json
import socket
import traceback
import logging

class MultiUserRCPSocketDServer():

    def __init__(self, socket_path=None, request_handler=None):
        self.socket_path = socket_path
        self.request_handler = request_handler

        self.logger = logging.getLogger("rpc_sockd_server")

    def read_chunk(self, conn, size):
        """
        Reads chunks of binary from conn up to size.

        Returns binary payload.
        """
        payload = b''
        while len(payload) < size:
            chunk = conn.recv(min(size - len(payload), 4096))
            if not chunk:
                break
            payload += chunk

        return payload

    def read(self, conn):
        """
        Returns decoded utf-8 json message text read from conn.
        """
        # First two bytes specify content length header length
        header_size_bytes = conn.recv(2)
        if not header_size_bytes:
            return

        # Next decode content length header.
        header_size = int.from_bytes(header_size_bytes, 'big')
        header_bytes = self.read_chunk(conn, header_size)

        header_json = header_bytes.decode('utf-8')
        header = json.loads(header_json)

        # Next read until content length.
        msg_bytes = self.read_chunk(conn, header['content_length'])
        return json.loads(msg_bytes.decode('utf-8'))

    # Server loop
    def serve(self, socket_path=None):
        if self.socket_path == None:
            self.socket_path = socket_path
    
        if os.path.exists(socket_path):
            os.remove(socket_path)
    
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(socket_path)
    
        # 660 so only owner/group can access
        os.chmod(socket_path, 0o660)
    
        sock.listen(128)
    
        self.logger.info(f"UserAgent listening on {socket_path}")
    
        while True:
            conn, _ = sock.accept()
    
            try:

                # Read message
                payload = self.read(conn)
                
                response = self.request_handler(payload)
    
# TODO: DO ENCODE WRAPPING HERE 
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


