import json
from app.services.cmd import Cmd
from app.config.config_manager import ConfigManager

class CmdService:
    """
    Service class for handling command operations including loading commands from JSON,
    applying exemptions, and filtering based on user permissions.
    """

    def __init__(self, commands_file = "json/commands.json", 
                 exemptions_file = "json/ctrl_exemptions.json"):
        """
        Initialize the CmdService.

        Args:
            commands_file (str): Path to the commands JSON file
            exemptions_file (str): Path to the command exemptions JSON file
        """
        self.commands_file = commands_file
        self.exemptions_file = exemptions_file
        self._commands_data = None
        self._exemptions_data = None
        self.config = ConfigManager()

    def load_data(self):
        """
        Load commands and exemptions data from JSON files.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.commands_file, "r") as commands_json:
                self._commands_data = json.load(commands_json)

            with open(self.exemptions_file, "r") as exemptions_json:
                self._exemptions_data = json.load(exemptions_json)

            return True

        except Exception as e:
            print(f"Problem reading command json files: {e}")
            return False

    def get_commands(self, server, current_user):
        """
        Get filtered list of commands for the specified server and user.

        Args:
            server (str): Name of game server to get commands for
            current_user (LocalProxy): Currently logged in flask user object

        Returns:
            List[Cmd]: List of command objects for server
        """
        if not self.load_data():
            return []

        # Create a working copy of commands data
        commands_dict = self._commands_data.copy()

        # Remove send command if disabled in config
        if self.config and not self.config.getboolean('settings', 'send_cmd'):
            commands_dict.pop("send", None)

        # Remove exempted commands for this server
        if self._exemptions_data and server in self._exemptions_data:
            for exempt_cmd in self._exemptions_data[server]:
                commands_dict.pop(exempt_cmd, None)

        # Filter commands based on user permissions
        return self._filter_commands_by_permissions(commands_dict, current_user)

    def _filter_commands_by_permissions(self, commands_dict, current_user):
        """
        Filter commands based on user role and permissions.

        Args:
            commands_dict (dict): Dictionary of commands to filter
            current_user (LocalProxy): Currently logged in flask user object

        Returns:
            List[Cmd]: Filtered list of command objects
        """
        commands = []

        # Load user permissions if not admin
        user_perms = {}
        if current_user.role != "admin":
            try:
                user_perms = json.loads(current_user.permissions)
            except (json.JSONDecodeError, AttributeError):
                user_perms = {}

        for long_cmd, cmd_data in commands_dict.items():
            # Skip if non-admin user doesn't have permission for this command
            if current_user.role != "admin":
                if long_cmd not in user_perms.get("controls", []):
                    continue

            # Create Cmd object
            cmd = Cmd()
            cmd.long_cmd = long_cmd
            cmd.short_cmd = cmd_data.get("short_cmd", "")
            cmd.description = cmd_data.get("description", "")
            commands.append(cmd)

        return commands

    def get_all_commands(self):
        """
        Get all commands without any filtering.

        Returns:
            List[Cmd]: List of all command objects
        """
        if not self.load_data():
            return []

        commands = []
        for long_cmd, cmd_data in self._commands_data.items():
            cmd = Cmd()
            cmd.long_cmd = long_cmd
            cmd.short_cmd = cmd_data.get("short_cmd", "")
            cmd.description = cmd_data.get("description", "")
            commands.append(cmd)

        return commands

    def get_command_by_long_name(self, long_cmd):
        """
        Get a specific command by its long name.

        Args:
            long_cmd (str): Long command name to search for

        Returns:
            Optional[Cmd]: Command object if found, None otherwise
        """
        if not self.load_data():
            return None

        cmd_data = self._commands_data.get(long_cmd)
        if not cmd_data:
            return None

        cmd = Cmd()
        cmd.long_cmd = long_cmd
        cmd.short_cmd = cmd_data.get("short_cmd", "")
        cmd.description = cmd_data.get("description", "")
        return cmd
