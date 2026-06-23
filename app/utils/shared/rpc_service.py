import os
import grp
import json
import socket
import traceback
import logging

class MultiUserRCPService():
    """
    The base class for the Mult-User JSON RPC service.
    """

    def __init__(self, socket_path=None, request_handler=None, logger=logging.getLogger("rpc_sockd_service")):
        self.socket_path = socket_path
        self.request_handler = request_handler
        self.logger = logger


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
        return msg_bytes.decode('utf-8')


    def encode(self, msg):
        """
        Takes utf-8 json msg and converts to padded custom binary format.
        """
        encoded = b''
        header = {
          'content_length': len(msg)
        }
        header_json = json.dumps(header)
        header_len = len(header_json)
        header_size = header_len.to_bytes(2, 'big')

        self.logger.info(header_len)
        self.logger.info(header_size)

        encoded += header_size
        encoded += header_json.encode()
        encoded += msg.encode()
        return encoded


    def send(self, msg, socket_path=None):
        """
        Sends payloads to socket.

        Returns result json from socket.
        """
        if self.socket_path == None:
            self.socket_path = socket_path

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.socket_path)

        encoded = self.encode(msg)

        self.logger.info(encoded)

        sock.sendall(encoded)

        response = self.read(sock)
        sock.close()

        data = json.loads(response)

        self.logger.info(data)

        if not data.get("ok"):
            raise RuntimeError(data.get("error"))

        return data.get("result")


    # Server loop
    def serve(self, socket_path=None):
        if self.socket_path == None:
            self.socket_path = socket_path

        if os.path.exists(socket_path):
            os.remove(socket_path)

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(socket_path)

        # 660 so only owner/group can access
#        os.chmod(socket_path, 0o660)

        sock.listen(128)

        self.logger.info(f"Listening on: {socket_path}")

        while True:
            conn, _ = sock.accept()

            try:
                # Read message
                payload = self.read(conn)
                self.logger.info(f"Payload: {payload}")

                # Run payload
                response = self.request_handler(json.loads(payload))

                # Return response
                response_json = json.dumps(response)
                encoded = self.encode(response_json)
                conn.sendall(encoded)

            except Exception as e:
                err = { 
                    "ok": False,
                    "error": "RPC Server Error",
                    "detail": str(e),
                }
                conn.sendall(self.encode(json.dumps(err)))

            finally:
                conn.close()

