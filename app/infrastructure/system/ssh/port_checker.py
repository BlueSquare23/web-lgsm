import socket

class PortChecker():

    def check(self, hostname, port=22):
        """ 
        Checks if a hostname/IP has an accessible SSH server on port.

        Args:
            hostname (str): The hostname or IP address to check.
            port (int): The port to check.

        Returns:
            bool: True if SSH is accessible, False otherwise.
        """
        timeout = 5 

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)

            result = sock.connect_ex((hostname, port))

            # Check the result: 0 means the port is open.
            if result == 0:
                return True
            else:
                return False
        except socket.gaierror:
            return False
        except socket.error:
            return False
        finally:
            sock.close()
