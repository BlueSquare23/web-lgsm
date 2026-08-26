class ListDir:

    def __init__(self, dir_manager):
        self.dir_manager = dir_manager

    def execute(self, server, directory, show_hidden):
        return self.dir_manager.list(server, directory, show_hidden)

