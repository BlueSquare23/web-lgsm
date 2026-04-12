class TemplateConfig:
    def __init__(self, config_manager):
        self._config = config_manager

    def get(self, section, option, fallback=None):
        return self._config.get(section, option, fallback)

    def getboolean(self, section, option, fallback=None):
        return self._config.getboolean(section, option, fallback)

    def getint(self, section, option, fallback=None):
        return self._config.getint(section, option, fallback)


class GetTemplateConfig:
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def execute(self):
        return TemplateConfig(self.config_manager)
