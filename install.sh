#!/usr/bin/env bash
# This install script downloads python3 and pip3 if necessary, it also sets up
# the project's python virtualenv and installs the necessary python modules.
# Written by John R., April 2023.

# Strict mode, close on any non-zero exit status.
set -eo pipefail

# In case script is invokes from outside of web-lgsm dir.
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH

# Debug mode.
[[ $1 =~ '-d' ]] && set -x && echo $EUID && ls -lah && printenv

# Colors!!!
red="\001\e[31m\002"
green="\001\e[32m\002"
yellow="\001\e[33m\002"
reset="\001\e[0m\002"

# Could break system python if pip is run as root.
if [[ "$EUID" -eq 0 ]]; then
    echo -e "${red}Do NOT run this script as root!${reset}"
    exit 1
fi

if [[ $(uname) != "Linux" ]]; then
    echo -e "${red}Only run install script on Debian or Ubuntu Linux!"
    exit 3
fi

if [[ ! -f '/etc/os-release' ]]; then
    echo -e "${red}No /etc/os-release file found!${reset}"
    echo -e "${red}Only run install script on Debian or Ubuntu Linux!${reset}"
    exit 3
fi

sys_name=$(grep -w 'NAME' /etc/os-release|cut -d= -f2|tr -d '"')

if [[ ! $sys_name =~ Ubuntu|Debian ]]; then
    echo -e "${red}Install Script Only Supports Debian & Ubuntu Linux!${reset}"
    echo -e "${yellow}See Readme.md for more info.${reset}"
    exit 3
fi

echo -e "${green}####### Pulling in apt updates...${reset}"
sudo apt-get update

for req in $(cat 'apt-reqs.txt'); do
    if ! sudo dpkg -l | grep -w "$req" &>/dev/null; then
        echo -e "${green}####### Installing \`$req\`...${reset}"
        sudo apt-get install -y $req
    fi
done

if ! which python3  &>/dev/null; then
    echo -e "${green}####### Installing \`python3\`...${reset}"
    sudo apt-get install -y python3
fi

if ! which pip3 &>/dev/null; then
    echo -e "${green}####### Installing \`pip3\`...${reset}"
    sudo apt-get install -y python3-pip

#    if [[ $sys_name =~ Ubuntu ]]; then
#        echo -e "${green}####### Upgrading \`pip3\`...${reset}"
#        python3 -m pip install --upgrade pip
#    fi
fi

echo -e "${green}####### Setting up Virtual Env...${reset}"
python3 -m venv venv
source venv/bin/activate

echo -e "${green}####### Install Requirements...${reset}"
python3 -m pip install -r requirements.txt

random_key=$(echo $RANDOM | md5sum | head -c 20)
echo "SECRET_KEY=\"$random_key\"" > .secret
chmod 600 .secret

# Setup sudoers rules to allow web-lgsm to run multi game server user
# management components without needing to prompt for a sudo pass.
echo -e "${green}####### Setting up Sudoers Rules...${reset}"

apb="$SCRIPTPATH/venv/bin/ansible-playbook"
venv_python="$SCRIPTPATH/venv/bin/python"
ansible_connector="$SCRIPTPATH/playbooks/sudo_ansible_connector.py"
create_sudo_rule="$SCRIPTPATH/playbooks/create_sudoers_rules.yml"
accpt_gs_users="$SCRIPTPATH/playbooks/vars/accepted_gs_users.yml"

# Hardcode web-lgsm system user into accepted_users validation list.
echo "  - $USER" >> $accpt_gs_users
echo "  - root" >> $accpt_gs_users
# Run sudo rule add playbook.
$apb -vvv $create_sudo_rule -e "gs_user='root'" -e "script_paths='$venv_python $ansible_connector'" -e "sudo_rule_name='$USER-$USER'" -e "web_lgsm_user='$USER'" -e "setup=true"

# Delete last line (aka root line) from accepted_gs_users.yml.
sed -i '$ d' $accpt_gs_users
# Lock playbook files down for security reasons.
sudo find $SCRIPTPATH/playbooks -type f -exec chmod 644 {} \;
sudo find $SCRIPTPATH/playbooks -type d -exec chmod 755 {} \;
sudo chmod 755 $apb $ansible_connector
sudo chown root:root $apb
sudo chown -R root:root $SCRIPTPATH/playbooks

echo -e "${green}####### Project Setup & Installation Complete!!!${reset}"
echo -e "${green}Run the \`web-lgsm.py\` script to start the server.${reset}"

