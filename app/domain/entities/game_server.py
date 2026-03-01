class GameServer:
    """
    Abstract domain layer representation of a GameServer.
    """
    def __init__(self, id, install_name, install_path, script_name, username, install_type, is_container=False, install_host=None, install_finished=None, install_failed=None, keyfile_path=None):
        self.id = id
        self.install_name = install_name
        self.install_path = install_path 
        self.script_name = script_name 
        self.username = username
        self.is_container = is_container
        self.install_type = install_type
        self.install_host = install_host
        self.install_finished = install_finished 
        self.install_failed = install_failed
        self.keyfile_path = keyfile_path

