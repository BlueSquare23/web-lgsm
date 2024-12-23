import json


class ProcInfoVessel:
    """
    Class used to create objects that hold information about processes launched
    via the subprocess Popen wrapper.
    """

    def __init__(self):
        """
        Args:
            stdout (list): Lines of stdout delivered by subprocess.Popen call.
            stderr (list): Lines of stderr delivered by subprocess.Popen call.
            process_lock (bool): Acts as lock to tell if process is still
                                 running and output is being appended.
            pid (int): Process id.
            exit_status (int): Exit status of cmd in Popen call.
        """
        self.stdout = []
        self.stderr = []
        self.process_lock = None
        self.pid = None
        self.exit_status = None

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def __str__(self):
        return f"ProcInfoVessel(stdout='{self.stdout}', stderr='{self.stderr}', process_lock='{self.process_lock}', pid='{self.pid}', exit_status='{self.exit_status}')"

    def __repr__(self):
        return f"ProcInfoVessel(stdout='{self.stdout}', stderr='{self.stderr}', process_lock='{self.process_lock}', pid='{self.pid}', exit_status='{self.exit_status}')"
