#!/bin/bash
# Uninstalls the web-lgsm base web application system files.

/usr/bin/sudo -v

## Debug / verbose mode.
[[ $1 =~ '-d' ]] && set -x

/usr/bin/sudo /usr/bin/rm -rf /opt/web-lgsm
/usr/bin/sudo /usr/bin/rm /usr/local/bin/ansible_connector.py
/usr/bin/sudo /usr/bin/rm -rf /usr/local/share/web-lgsm
/usr/bin/sudo /usr/bin/rm /etc/sudoers.d/$USER-$USER

set +x 

## Headless  mode.
[[ $1 =~ '-h' ]] && exit

echo -e "$green ✓ $reset Web-LGSM System Components Removed!"
echo "Simply remove the web-lgsm directory to complete the uninstall."
