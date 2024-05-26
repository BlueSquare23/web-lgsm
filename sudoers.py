import re
import shutil
import tempfile
import subprocess

def update_sudoers(user1, user2, command_string):
    new_line = f"{user1} ALL=({user2}) NOPASSWD: {command_string}\n"
    sudoers_file = '/etc/sudoers'
    temp_sudoers_file = tempfile.mktemp()

    with open(sudoers_file, 'r') as f:
        lines = f.readlines()

    pattern = re.compile(rf"^{re.escape(user1)}\s+ALL=\({re.escape(user2)}\)\s+NOPASSWD:")
    found = False

    with open(temp_sudoers_file, 'w') as f:
        for line in lines:
            if pattern.match(line):
                f.write(new_line)
                found = True
            else:
                f.write(line)
        if not found:
            f.write(new_line)

    # Validate the new sudoers file
    result = subprocess.run(['visudo', '-c', '-f', temp_sudoers_file], capture_output=True, text=True)

    if result.returncode == 0:
        # If valid, move the temporary file to the actual sudoers file
        shutil.move(temp_sudoers_file, sudoers_file)
        print("Sudoers file updated successfully.")
    else:
        print("Failed to validate the new sudoers file.")
        print(result.stderr)

# Example usage
#update_sudoers('user1', 'user2', '/path/to/command1')

