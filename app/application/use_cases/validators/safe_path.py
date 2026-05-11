import os
from pathlib import Path

class IsSafePath:

    def __init__(self, dir_manager):
        self.dir_manager = dir_manager

    def execute(self, server, path):
        if not self.dir_manager.traversal_safe(server, path):
            return False

        # Check if it's excluded.
        if self.dir_manager.check_excluded(server, path):
            return False

        return True

