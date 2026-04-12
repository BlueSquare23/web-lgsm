from app.utils.paths import PATHS

from app.infrastructure.system.repositories.proc_info_repo import InMemProcInfoRepository

from app.infrastructure.system.command_executor.command_executor import CommandExecutor

class SudoersService():
    """
    Class for interacting with web-lgsm system USER sudoers rules.

    Used by add route for automatically adding sudoers rules if they don't
    already exist.
    """
    CONNECTOR_CMD = [
        PATHS["sudo"],
        "-n",
        "/opt/web-lgsm/bin/python",
        PATHS["ansible_connector"],
    ]

    def __init__(self):
        self.command_service = CommandExecutor()

    def has_access(self, username):
        cmd = [PATHS['sudo'], '-n', '-l']
        cmd_id = 'check_sudo_access'
        success = self.command_service.run(cmd, None, cmd_id)
        proc_info = InMemProcInfoRepository().get(cmd_id)

        if not success or proc_info == None:
            return False

        for line in proc_info.stdout:
            if f'({username}) NOPASSWD: ALL' in line:
                return True

        return False

    def add_user(self, username):
        """
        Run playbook to add sudoers users.
        """

        cmd = SudoersService.CONNECTOR_CMD + ["--user", username]
        cmd_id = f'add_sudoers_rule_{username}'
        self.command_service.run(cmd, None, cmd_id)
        proc_info = InMemProcInfoRepository().get(cmd_id)

        if proc_info == None:
            return False

        if proc_info.exit_status > 0:
            return False

        return True

