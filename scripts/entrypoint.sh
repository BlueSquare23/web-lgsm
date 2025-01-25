#!/usr/bin/env bash
# Docker entrypoint wrapper script.

printenv
set -xe

# Start the SSH service.
service ssh start

export HOME=/home/web-lgsm
cd $HOME

# Use exec to replace this scripts pid with web-lgsm pid.
exec sudo -E -u web-lgsm /home/web-lgsm/web-lgsm.py --start
