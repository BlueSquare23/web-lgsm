import json

from app.domain.entities.control import Control 
from app.infrastructure.system.config.config_manager import ConfigManager

class ControlsRepository(Control):
    """
    Service class for handling control operations including loading controls from JSON,
    applying exemptions, and filtering based on user permissions.
    """

    def __init__(self, controls_file = "json/controls.json", 
                 exemptions_file = "json/control_exemptions.json"):
        """
        Initialize Controls.

        Args:
            controls_file (str): Path to the controls JSON file
            exemptions_file (str): Path to the control exemptions JSON file
        """
        self.controls_file = controls_file
        self.exemptions_file = exemptions_file
        self._controls_data = None
        self._exemptions_data = None
        self.config = ConfigManager()

    def load_data(self):
        """
        Load controls and exemptions data from JSON files.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.controls_file, "r") as controls_json:
                self._controls_data = json.load(controls_json)

            with open(self.exemptions_file, "r") as exemptions_json:
                self._exemptions_data = json.load(exemptions_json)

            return True

        except Exception as e:
            print(f"Problem reading control json files: {e}")
            return False

    def list(self, server, user):
        """
        Get filtered list of controls for the specified server and user.

        Args:
            server (str): Name of game server to get controls for
            user (User): User domain object for current flask user

        Returns:
            List[Control]: List of control objects for server
        """
        if not self.load_data():
            return []

        # Create a working copy of controls data
        controls_dict = self._controls_data.copy()

        # Remove send control if disabled in config
        if self.config and not self.config.getboolean('settings', 'send_cmd'):
            controls_dict.pop("send", None)

        # Remove exempted controls for this server
        if self._exemptions_data and server in self._exemptions_data:
            for exempt_ctrl in self._exemptions_data[server]:
                controls_dict.pop(exempt_ctrl, None)

        # Filter controls based on user permissions
        return self._filter_controls_by_permissions(controls_dict, user)

    def _filter_controls_by_permissions(self, controls_dict, user):
        """
        Filter controls based on user role and permissions.

        Args:
            controls_dict (dict): Dictionary of controls to filter
            user (User): User domain object for current flask user

        Returns:
            List[Control]: Filtered list of control objects
        """
        controls = []

        # Load user permissions if not admin
        user_perms = {}
        if user.role != "admin":
            try:
                user_perms = json.loads(user.permissions)
            except (json.JSONDecodeError, AttributeError):
                user_perms = {}

        for long_ctrl, ctrl_data in controls_dict.items():
            # Skip if non-admin user doesn't have permission for this control
            if user.role != "admin":
                if long_ctrl not in user_perms.get("controls", []):
                    continue

            # Create Control object
            ctrl = Control()
            ctrl.long_ctrl = long_ctrl
            ctrl.short_ctrl = ctrl_data.get("short_ctrl", "")
            ctrl.description = ctrl_data.get("description", "")
            controls.append(ctrl)

        return controls

