class CancelGameServerInstall:

    def __init__(self, install_manager):
        self.install_manager = install_manager

    def execute(self, pid):
        """
        Returns:
            Bool: True if install canceled successfully, False otherwise.
        """
        return self.install_manager.cancel(pid)

