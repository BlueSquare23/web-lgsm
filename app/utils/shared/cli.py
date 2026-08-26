import sys
import json

from .find_cfg_paths import find_cfg_paths
from .read_file import read_file
from .write_file import write_file
from .delete_file import delete_file
from .rename_file import rename_file
from .edit_cron import edit_cron
from .list_dir import list_dir
from .is_excluded import is_excluded
from .traversal_safe import traversal_safe

# functions mapping
functions = {
    "find_cfg_paths": find_cfg_paths,
    "read_file": read_file,
    "write_file": write_file,
    "delete_file": delete_file,
    "rename_file": rename_file,
    "edit_cron": edit_cron,
    "list_dir": list_dir,
    "is_excluded": is_excluded,
    "traversal_safe": traversal_safe,
}

if __name__ == "__main__":
    raw_input = sys.stdin.buffer.read()

    if not raw_input.strip():
        raise ValueError("No JSON input provided on stdin")

    data = json.loads(raw_input)

    func_name = data["func"]
    args = data.get("args", [])
    kwargs = data.get("kwargs", {})

    if func_name not in functions:
        raise ValueError(f"Unknown function: {func_name}")

    result = functions[func_name](*args, **kwargs)

    print(json.dumps(result))

