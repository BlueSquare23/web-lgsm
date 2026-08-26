class IsDir:

    def __init__(self, dir_manager):
        self.dir_manager = dir_manager

    def execute(self, server, path):
        return self.dir_manager.is_dir(server, path)

