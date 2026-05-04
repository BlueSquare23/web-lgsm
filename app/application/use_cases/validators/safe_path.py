import os
from pathlib import Path

class SafePath:

    def execute(self, path, username):
        base_dir = Path(f"/home/{username}").resolve()
        target_path = Path(path).resolve()

        try:
            target_path.relative_to(base_dir)
            return True
        except ValueError:
            return False

