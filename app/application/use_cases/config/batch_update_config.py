class BatchUpdateConfig:

    def __init__(self, config_manager):
        self.config_manager = config_manager

    def execute(self):
        return self.config_manager.batch_update()

