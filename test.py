#!/usr/bin/env python3
# Stand alone install script testing...

import os
import sys
import subprocess

def run_cmd(cmd, exec_dir=os.getcwd()):
    try:
        proc = subprocess.Popen(cmd,
                cwd=exec_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
        )

        for stdout_line in iter(proc.stdout.readline, ""):
            print(stdout_line, end="", flush=True)

        for stderr_line in iter(proc.stderr.readline, ""):
            print(stderr_line, end="", flush=True)

        print(f"Command '{cmd}' executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Command '{cmd}' failed with return code {e.returncode}.")
        print("Error output:", e.stderr)
    except FileNotFoundError:
        print(f"Command '{cmd}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred while running '{cmd}': {str(e)}")

def main(argv):
    if len(sys.argv) < 4:
        print("Usage: test.py 'cmd1' 'cmd2' 'cmd3'")
        sys.exit(1)

    cmd1 = argv[0].split(',')
    cmd2 = argv[1].split(',')
    cmd3 = argv[2].split(',')

    run_cmd(cmd1)
    run_cmd(cmd2, '/home/mcserver/Minecraft/')
    run_cmd(cmd3)

if __name__ == "__main__":
    main(sys.argv[1:])
