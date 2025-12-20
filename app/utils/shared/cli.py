import sys
import json
from .find_cfg_paths import find_cfg_paths
from .read_file import read_file
from .write_file import write_file

if __name__ == "__main__":
    # Parse command line arguments.
    data = json.loads(sys.argv[1])
    func_name = data['func']
    args = data['args']
    kwargs = data['kwargs']

    results = dict()
    
    # Call the function.
    if func_name == 'find_cfg_paths':
        result = find_cfg_paths(*args, **kwargs)

    if func_name == 'read_file':
        result = read_file(*args, **kwargs)

    if func_name == 'write_file':
        result = write_file(*args, **kwargs)

    print(json.dumps(result))
