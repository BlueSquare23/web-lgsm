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
        self._batch_mode = False
        self._pending_writes = False
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

    def set(self, section, option, value, immediate=True):
        if not self._config.has_section(section):
            self._config.add_section(section)
        self._config[section][option] = str(value)

        if immediate and not self._batch_mode:
            self._write_config()
        else:
            self._pending_writes = True

    def batch_update(self):
        """Context manager for multiple updates with single write"""
        return self.BatchUpdateContext(self)

    class BatchUpdateContext:
        def __init__(self, config):
            self.config = config

        def __enter__(self):
            self.config._batch_mode = True
            return self.config

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.config._batch_mode = False
            if self.config._pending_writes:
                self.config._write_config()
                self.config._pending_writes = False

    def _write_config(self):
        with open(self.config_file, 'w') as configfile:
            self._config.write(configfile)
