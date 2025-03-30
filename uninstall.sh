#!/bin/bash
# Uninstalls the web-lgsm base web application system files.

# Colors!!!
red="\001\e[31m\002"
green="\001\e[32m\002"
reset="\001\e[0m\002"

# Could break system python if pip is run as root.
if [[ "$EUID" -eq 0 ]]; then
    echo -e "${red}Don't run this script as root!${reset}"
    exit 1
fi

sudo -v

## Debug / verbose mode.
[[ $1 =~ '-d' ]] && set -x

sudo rm -rf /opt/web-lgsm
sudo rm /usr/local/bin/ansible_connector.py
sudo rm -rf /usr/local/share/web-lgsm
sudo rm /etc/sudoers.d/$USER-$USER

set +x 

echo -e "$green ✓ $reset Web-LGSM System Components Removed!"
echo "Simply remove the web-lgsm directory to complete the uninstall."
