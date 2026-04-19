class DeleteFile:

    def __init__(self, file_manager):
        self.file_manager = file_manager

    def execute(self, server, file_path):
        return self.file_manager.delete(server, file_path)

