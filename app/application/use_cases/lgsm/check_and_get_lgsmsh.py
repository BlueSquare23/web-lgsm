
class CheckAndGetLgsmsh:
    def __init__(self, lgsm_manager):
        self.lgsm_manager = lgsm_manager

    def execute(self, lgsmsh_path):
        """
        Use case for ensuring linuxgsm.sh is present and up-to-date.
        """
        self.lgsm_manager.check_and_get_lgsmsh(lgsmsh_path)
