from app.utils.paths import PATHS
from app.config.config_manager import ConfigManager

from .proc_info_service.proc_info_service import ProcInfoService
from .command_exec_service.command_exec_service import CommandExecService


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

    def __init__(self, username):
        self.username = username
        self.command_service = CommandExecService(ConfigManager())

    def has_access(self):
        cmd = [PATHS['sudo'], '-n', '-l']
        cmd_id = 'check_sudo_access'
        success = self.command_service.run_command(cmd, None, cmd_id)
        proc_info = ProcInfoService().get_process(cmd_id)

        if not success or proc_info == None:
            return False

        for line in proc_info.stdout:
            if f'({self.username}) NOPASSWD: ALL' in line:
                return True

        return False

    def add_user(self):
        """
        Run playbook to add sudoers users.
        """
        cmd = SudoersService.CONNECTOR_CMD + ["--user", self.username]
        cmd_id = f'add_sudoers_rule_{self.username}'
        self.command_service.run_command(cmd, None, cmd_id)
        proc_info = ProcInfoService().get_process(cmd_id)

        if proc_info == None:
            return False

        if proc_info.exit_status > 0:
            return False

        return True

