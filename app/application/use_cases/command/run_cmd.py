class RunCommand:

    def __init__(self, command_executor):
        self.command_executor = command_executor

    def execute(self, cmd, server=None, cmd_id=None, app_context=False):
        return self.command_executor.run(cmd, server, cmd_id, app_context)

