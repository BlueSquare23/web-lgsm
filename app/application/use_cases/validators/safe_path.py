import os
from pathlib import Path

class IsSafePath:

    def __init__(self, dir_manager):
        self.dir_manager = dir_manager

    def execute(self, server, path):
        base_dir = Path(f"/home/{server.username}").resolve()
        target_path = Path(path).resolve()

        # Check is below game server user home dir.
        try:
            target_path.relative_to(base_dir)
        except ValueError:
            return False

        # Check if it's excluded.
        if self.dir_manager.check_excluded(server, path):
            return False

        return True

