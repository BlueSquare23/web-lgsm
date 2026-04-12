class WriteFile:

    def __init__(self, file_manager):
        self.file_manager = file_manager

    def execute(self, server, file_path, content):
        return self.file_manager.write(server, file_path, content)

