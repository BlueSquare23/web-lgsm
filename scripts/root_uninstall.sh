#!/bin/bash
# Uninstalls the web-lgsm base system files as root as part of unattended
# update system.
# Written by John R., Aug 2025.

# Safe PATH.
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin"

# Strict mode, close on any non-zero exit status.
set -eo pipefail

# Root check.
if [[ "$EUID" -ne 0 ]]; then
    echo "Must be run as root" >&2
    exit 1
fi

## Debug mode.
[[ "$@" =~ '-d' ]] && set -x

USERNAME=$(cat "/usr/local/share/web-lgsm/install_conf.json" | jq '.USERNAME')
if [[ -z $USERNAME ]]; then
    echo "Failed to parse install_conf.json!" >&2
    exit 9
fi

rm -rf /opt/web-lgsm
rm /usr/local/bin/ansible_connector.py
rm -rf /usr/local/share/web-lgsm
rm /etc/sudoers.d/$USERNAME-$USERNAME

set +x 

## Verbose mode.
if [[ "$@" =~ '-v' ]]; then
    echo -e "$green ✓ $reset Web-LGSM System Components Removed!"
    echo "Simply remove the web-lgsm directory to complete the uninstall."
fi
