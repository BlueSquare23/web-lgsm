class CleanupDownload:

    def __init__(self, file_manager):
        self.file_manager = file_manager

    def execute(self, server, tmp_path):
        return self.file_manager.cleanup_download(server, tmp_path)
