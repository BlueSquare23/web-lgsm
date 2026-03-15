class GetIntConfig:

    def __init__(self, config_manager):
        self.config_manager = config_manager

    def execute(self, section, option, fallback=None):
        return self.config_manager.getint(section, option, fallback)

