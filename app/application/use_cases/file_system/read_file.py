class ReadFile:

    def __init__(self, file_manager):
        self.file_manager = file_manager

    def execute(self, server, file_path):
        return self.file_manager.read(server, file_path)

