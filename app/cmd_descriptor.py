class CmdDescriptor:
    """
    Class used to create objects for holding command descriptions. Used by the
    get_commands() util function.

    Args:
        long_cmd (str): Long form of a command (for example "start")
        short_cmd (str): Short form of a command (for example "st")
        description (str): A description of what the command does.
    """

    def __init__(self):
        self.long_cmd = ""
        self.short_cmd = ""
        self.description = ""

    def __str__(self):
        return f"CmdDescriptor(long_cmd='{self.long_cmd}', short_cmd='{self.short_cmd}', description='{self.description}')"

    def __repr__(self):
        return f"CmdDescriptor(long_cmd='{self.long_cmd}', short_cmd='{self.short_cmd}', description='{self.description}')"

