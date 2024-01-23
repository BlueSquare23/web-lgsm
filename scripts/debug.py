#!/usr/bin/env python3
# Script for starting the server in debug mode. Useful for debugging /
# developing. Written by John R., Jan. 2024.

import os
try:
    os.environ["VIRTUAL_ENV"]
except KeyError:
    exit(" [!] Not in virtual env!\n" +
         "Run the following, then re-run this script.\n" +
         "\tsource venv/bin/activate")
import sys
# App path up above scripts dir.
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')
from app import main

if __name__ == "__main__":
    app = main()
    app.run(debug=True, host="0.0.0.0")
