class CancelGameServerInstall:

    def __init__(self, game_server_manager):
        self.game_server_manager = game_server_manager

    def execute(self, pid):
        """
        Returns:
            Bool: True if install canceled successfully, False otherwise.
        """
        return self.game_server_manager.cancel_install(pid)

