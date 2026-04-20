import sys
import json
from .find_cfg_paths import find_cfg_paths
from .read_file import read_file
from .write_file import write_file
from .delete_file import write_file
from .rename_file import write_file
from .edit_cron import edit_cron

if __name__ == "__main__":
    # Parse command line arguments.
    data = json.loads(sys.argv[1])
    func_name = data['func']
    args = data['args']
    kwargs = data['kwargs']

    results = dict()

    # TODO: Find a better way to pack this that's less redundant.
    # Call the function.
    if func_name == 'find_cfg_paths':
        result = find_cfg_paths(*args, **kwargs)

    if func_name == 'read_file':
        result = read_file(*args, **kwargs)

    if func_name == 'write_file':
        result = write_file(*args, **kwargs)

    if func_name == 'delete_file':
        result = delete_file(*args, **kwargs)

    if func_name == 'rename_file':
        result = rename_file(*args, **kwargs)

    if func_name == 'edit_cron':
        result = edit_cron(*args, **kwargs)

    print(json.dumps(result))
