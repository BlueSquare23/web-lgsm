class Control:
    """
    Data class used for describing Control objects for game servers controls
    page.

    Args:
        long_ctrl (str): Long form of a control (for example "start")
        short_ctrl (str): Short form of a control (for example "st")
        description (str): A description of what the control does.
    """

    def __init__(self):
        self.long_ctrl = ""
        self.short_ctrl = ""
        self.description = ""

    # TODO: Make this not just the same as repr someday
    def __str__(self):
        return f"Control(long_ctrl='{self.long_ctrl}', short_ctrl='{self.short_ctrl}', description='{self.description}')"

    def __repr__(self):
        return f"Control(long_ctrl='{self.long_ctrl}', short_ctrl='{self.short_ctrl}', description='{self.description}')"

