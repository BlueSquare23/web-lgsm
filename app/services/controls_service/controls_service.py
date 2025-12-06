import json
from .control import Control 
from app.config.config_manager import ConfigManager

class ControlService:
    """
    Service class for handling control operations including loading controls from JSON,
    applying exemptions, and filtering based on user permissions.
    """

    def __init__(self, controls_file = "json/controls.json", 
                 exemptions_file = "json/control_exemptions.json"):
        """
        Initialize the ControlService.

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

    def get_controls(self, server, current_user):
        """
        Get filtered list of controls for the specified server and user.

        Args:
            server (str): Name of game server to get controls for
            current_user (LocalProxy): Currently logged in flask user object

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
        return self._filter_controls_by_permissions(controls_dict, current_user)

    def _filter_controls_by_permissions(self, controls_dict, current_user):
        """
        Filter controls based on user role and permissions.

        Args:
            controls_dict (dict): Dictionary of controls to filter
            current_user (LocalProxy): Currently logged in flask user object

        Returns:
            List[Control]: Filtered list of control objects
        """
        controls = []

        # Load user permissions if not admin
        user_perms = {}
        if current_user.role != "admin":
            try:
                user_perms = json.loads(current_user.permissions)
            except (json.JSONDecodeError, AttributeError):
                user_perms = {}

        for long_ctrl, ctrl_data in controls_dict.items():
            # Skip if non-admin user doesn't have permission for this control
            if current_user.role != "admin":
                if long_ctrl not in user_perms.get("controls", []):
                    continue

            # Create Control object
            ctrl = Control()
            ctrl.long_ctrl = long_ctrl
            ctrl.short_ctrl = ctrl_data.get("short_ctrl", "")
            ctrl.description = ctrl_data.get("description", "")
            controls.append(ctrl)

        return controls

    def get_all_controls(self):
        """
        Get all controls without any filtering.

        Returns:
            List[Control]: List of all control objects
        """
        if not self.load_data():
            return []

        controls = []
        for long_ctrl, ctrl_data in self._controls_data.items():
            ctrl = Control()
            ctrl.long_ctrl = long_ctrl
            ctrl.short_ctrl = ctrl_data.get("short_ctrl", "")
            ctrl.description = ctrl_data.get("description", "")
            controls.append(ctrl)

        return controls

    def get_control_by_long_name(self, long_ctrl):
        """
        Get a specific control by its long name.

        Args:
            long_ctrl (str): Long control name to search for

        Returns:
            Optional[Control]: Command object if found, None otherwise
        """
        if not self.load_data():
            return None

        ctrl_data = self._controls_data.get(long_ctrl)
        if not ctrl_data:
            return None

        ctrl = Control()
        ctrl.long_ctrl = long_ctrl
        ctrl.short_ctrl = ctrl_data.get("short_ctrl", "")
        ctrl.description = ctrl_data.get("description", "")
        return ctrl
