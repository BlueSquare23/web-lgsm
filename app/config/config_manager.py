import os
import configparser
from .defaults import DEFAULTS

class ConfigManager:
    """
    Config manager class for project's main.conf(.local) INI style config file.

    Custom class for dynamic config info to provide similar interface as
    builtin flask app.config.
    """
    # Class level defaults.
    _DEFAULTS = DEFAULTS

    def __init__(self):
        self.config_file = "main.conf"
        self.config_local = "main.conf.local"

        # Local config override.
        if os.path.isfile(self.config_local) and os.access(self.config_local, os.R_OK):
            self.config_file = self.config_local

        self._config = configparser.ConfigParser()
        self.reload()

    def reload(self):
        self._config.read(self.config_file)

    def get(self, section, option, fallback=None):
        self.reload()  # Real-time reloading on every access

        if fallback is None:
            fallback = self._get_default(section, option)

        return self._config[section].get(option, fallback)

    def _get_default(self, section, option):
        try:
            default_value = self._DEFAULTS[section][option]
            return default_value
        except KeyError:
            return None

    def getboolean(self, section, option, fallback=None):
        self.reload()
        return self._config[section].getboolean(option, fallback)

    def getint(self, section, option, fallback=None):
        self.reload()
        return self._config[section].getint(option, fallback)

    def __getitem__(self, section):
        self.reload()
        return self._config[section]
