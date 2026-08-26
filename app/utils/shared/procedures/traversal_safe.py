import os
import pwd
from pathlib import Path

def traversal_safe(path):
    """
    General purpose is traversal attempt checker.

    Returns:
        bool: True if NOT dir traversal attempt. In other words True if
              valid path, False otherwise.
    """
    # Look up the real home dir via the passwd db rather than trusting the
    # $HOME env var (Path.home()), since $HOME can be overridden by whatever
    # launched this process (e.g. CI jobs setting HOME to the checkout dir),
    # which would silently break this security boundary.
    current_home = pwd.getpwuid(os.geteuid()).pw_dir
    base_dir = Path(current_home).resolve()
    candidate = (base_dir / path).resolve()

    try:
        candidate.relative_to(base_dir)
    except ValueError:
        return False

    return True

