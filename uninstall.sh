#!/bin/bash
# Uninstalls the web-lgsm application system files.
# Does NOT remove the web-lgsm app dir.

/usr/bin/sudo -v

## Debug / verbose mode.
[[ "$@" =~ '-d' ]] && set -x

/usr/bin/sudo /usr/bin/rm -rf /opt/web-lgsm
/usr/bin/sudo /usr/bin/rm /usr/local/bin/ansible_connector.py
/usr/bin/sudo /usr/bin/rm -rf /usr/local/share/web-lgsm
/usr/bin/sudo /usr/bin/rm /etc/sudoers.d/$USER-$USER
/usr/bin/sudo /usr/bin/rm -rf /run/web-lgsm

set +x 

## Headless  mode, quit before print.
[[ "$@" =~ '-h' ]] && exit

green="\001\e[32m\002"
reset="\001\e[0m\002"

echo -e "$green ✓ $reset Web-LGSM system components removed!"
echo "Simply remove the web-lgsm directory to complete the uninstall."
