#!/usr/bin/env bash
# This install script downloads python3 and pip3 if necessary, it also sets up
# the project's python virtualenv and installs the necessary python modules.
# Written by John R., April 2023.

# Strict mode, close on any non-zero exit status.
set -eo pipefail

# In case script is invokes from outside of web-lgsm dir.
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH

set -x

source venv/bin/activate

echo -e "${green}####### Setting up Sudoers Rules...${reset}"

apb="$SCRIPTPATH/venv/bin/ansible-playbook"
del_user="$SCRIPTPATH/playbooks/delete_user.yml"
create_sudo_rule="$SCRIPTPATH/playbooks/create_sudoers_rules.yml"
inst_new_gs="$SCRIPTPATH/playbooks/install_new_game_server.yml"
script_paths="$apb $del_user *, $apb $create_sudo_rule *, $apb $inst_new_gs *"
accpt_gs_users="$SCRIPTPATH/playbooks/vars/accepted_gs_users.yml"
echo "  - $USER" >> $accpt_gs_users
echo "  - root" >> "$SCRIPTPATH/playbooks/vars/accepted_gs_users.yml"
$apb -vvv $create_sudo_rule -e "gs_user='root'" -e "script_paths='$script_paths'" -e "sudo_rule_name='$USER-$USER'" -e "web_lgsm_user='$USER'" -e "setup=true"
sed -i '$ d' $accpt_gs_users
## Lock playbook files down for sec reasons.
#sudo find $SCRIPTPATH/playbooks -type f -exec chmod 644 {} \;
#sudo find $SCRIPTPATH/playbooks -type d -exec chmod 755 {} \;
#sudo chown -R root:root $SCRIPTPATH/playbooks

echo -e "${green}####### Project Setup & Installation Complete!!!${reset}"
echo -e "${green}Run the \`web-lgsm.py\` script to start the server.${reset}"

