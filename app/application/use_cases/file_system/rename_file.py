class RenameFile:

    def __init__(self, file_manager):
        self.file_manager = file_manager

    def execute(self, server, file_path, new_name):
        return self.file_manager.rename(server, file_path, new_name)

