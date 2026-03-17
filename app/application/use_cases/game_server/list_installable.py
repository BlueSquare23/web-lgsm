class ListInstallableGameServers:

    def __init__(self, install_manager):
        self.install_manager = install_manager

    def execute(self):
        return self.install_manager.list()

