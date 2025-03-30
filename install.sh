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

# Docker install.
if [[ $1 =~ '--docker' ]]; then
    # Literally just stealing the install from the docker docs.
    # https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
    echo -e "${green}####### Install Apt Docker Components...${reset}"

    # Add Docker's official GPG key:
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
    
    # Add the repository to Apt sources:
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update

    echo -e "${green}####### Docker install completed successfully!${reset}"
    exit
fi

# Needs curl to get lgsm apt reqs.
if ! which curl &>/dev/null; then
    echo -e "${green}####### Installing \`curl\`...${reset}"
    sudo apt-get install -y curl
fi

# Function to detect the Ubuntu or Debian version
detect_distro_version() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        if [ "$ID" == "ubuntu" ] || [ "$ID" == "debian" ]; then
            echo "$ID-$VERSION_ID"
        else
            echo "Unsupported distribution: $ID"
            exit 1
        fi
    else
        echo "Cannot detect the distribution."
        exit 1
    fi
}

# List of supported versions
supported_versions=(
    "ubuntu-18.04"
    "ubuntu-20.04"
    "ubuntu-22.04"
    "ubuntu-23.04"
    "ubuntu-23.10"
    "ubuntu-24.04"
    "debian-10"
    "debian-11"
    "debian-12"
    "debian-13"
)

# Detect the current distribution and version
distro_version=$(detect_distro_version)

# Check if the detected version is supported
if [[ " ${supported_versions[*]} " == *" $distro_version "* ]]; then
    echo "Detected supported version: $distro_version"
else
    echo "Unsupported version: $distro_version"
    exit 1
fi

# GitHub base URL for the CSV files.
github_base_url="https://raw.githubusercontent.com/GameServerManagers/LinuxGSM/refs/heads/master/lgsm/data"

# Construct the full URL for the CSV file.
csv_url="$github_base_url/$distro_version.csv"

# Download the CSV file.
echo "Downloading $csv_url..."
apt_csv=$(curl -s "$csv_url")

# Check if the download was successful.
if [ $? -eq 0 ]; then
    echo "Downloaded $distro_version.csv successfully."
else
    echo "Failed to download $distro_version.csv."
    rm -f "$temp_csv"
    exit 1
fi

all_reqs_csv=$(grep 'all,' <<< "$apt_csv")
all_reqs=$(tr ',' "\n" <<< "$all_reqs_csv")

# Append lgsm requirements to web-lgsm apt reqs.
echo "$all_reqs" >> 'apt-reqs.txt'

# Install apt requirements!
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
fi

echo -e "${green}####### Setting up Virtual Env...${reset}"
python3 -m venv venv
source venv/bin/activate

if [[ $sys_name =~ Ubuntu ]]; then
    echo -e "${green}####### Upgrading \`pip3\`...${reset}"
    python3 -m pip install --upgrade pip
fi

echo -e "${green}####### Installing Python Requirements...${reset}"
python3 -m pip install -r requirements.txt

echo -e "${green}####### Installing NPM Requirements...${reset}"
cd $SCRIPTPATH/app/static/js
npm install @xterm/xterm
npm install --save @xterm/addon-fit
cd $SCRIPTPATH

# Setup sudoers rules to allow web-lgsm to run multi game server user
# management components without needing to prompt for a sudo pass.
echo -e "${green}####### Setting up Sudoers Rules...${reset}"

apb="$SCRIPTPATH/venv/bin/ansible-playbook"
venv_python="$SCRIPTPATH/venv/bin/python"
ansible_connector="$SCRIPTPATH/playbooks/ansible_connector.py"
accpt_usernames="$SCRIPTPATH/playbooks/vars/accepted_usernames.yml"
web_lgsm_user_vars="$SCRIPTPATH/playbooks/vars/web_lgsm_user.yml"
sudoers_file="/etc/sudoers.d/$USER-$USER"

# Hardcode web-lgsm system user into accepted_users validation list and
# web_user ansible vars files.
echo "  - $USER" >> $accpt_usernames
echo "web_lgsm_user: $USER" > $web_lgsm_user_vars

# Write sudoers rule for passwordless install & delete.
sudoers_rule="$USER ALL=(root) NOPASSWD: $venv_python $ansible_connector *"
temp_sudoers=$(mktemp)
echo "$sudoers_rule" > "$temp_sudoers"
sudo chmod 0440 "$temp_sudoers"
sudo chown root:root "$temp_sudoers"
sudo visudo -cf "$temp_sudoers"  # Validate new file.
sudo mv "$temp_sudoers" "$sudoers_file"

# Lock playbook files down for security reasons.
sudo find $SCRIPTPATH/playbooks -type f -exec chmod 644 {} \;
sudo find $SCRIPTPATH/playbooks -type d -exec chmod 755 {} \;
sudo chmod 755 $apb $ansible_connector
sudo chown -R root:root $apb "$SCRIPTPATH/playbooks"
# Can't make files immutable in containers.
if [[ -z $CONTAINER ]]; then
    sudo chattr +i $apb $ansible_connector
fi

# Finally setup random key.
random_key=$(echo $RANDOM | md5sum | head -c 20)
echo "SECRET_KEY=\"$random_key\"" > .secret
chmod 600 .secret

echo -e "${green}####### Project Setup & Installation Complete!!!${reset}"
echo -e "${green}Run the \`web-lgsm.py\` script to start the server.${reset}"
