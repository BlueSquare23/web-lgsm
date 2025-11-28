class Control:
    """
    Class used to create objects for holding command descriptions. Used by the
    get_controls() util function.

    Args:
        long_ctrl (str): Long form of a command (for example "start")
        short_ctrl (str): Short form of a command (for example "st")
        description (str): A description of what the command does.
    """

    def __init__(self):
        self.long_ctrl = ""
        self.short_ctrl = ""
        self.description = ""

    # TODO: Make this not just the same as repr someday
    def __str__(self):
        return f"Cmd(long_ctrl='{self.long_ctrl}', short_ctrl='{self.short_ctrl}', description='{self.description}')"

    def __repr__(self):
        return f"Cmd(long_ctrl='{self.long_ctrl}', short_ctrl='{self.short_ctrl}', description='{self.description}')"

