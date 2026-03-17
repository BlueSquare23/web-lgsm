
class ClearInstallBufferOutput:

    def __init__(self, install_manager):
        self.install_manager = install_manager

    def execute(self, server_id, app_context):
        """
        Returns:
            Bool: True if install canceled successfully, False otherwise.
        """
        return self.clear_proc_info_post_install(server_id, app_context)
