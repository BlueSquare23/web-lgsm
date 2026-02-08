#!/usr/bin/env bash
# Installs apt pkgs, ansible scripts, and other things as root for the
# web-lgsm application.
# Written by John R., Aug 2025.

# Strict mode, close on any non-zero exit status.
set -eo pipefail

# Safe PATH.
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin"

# Debug mode.
[[ $1 =~ '-d' ]] && set -x && echo $EUID && ls -lah && printenv

## Globals.

# Colors!
RED="\001\e[31m\002"
GREEN="\001\e[32m\002"
YELLOW="\001\e[33m\002"
RESET="\001\e[0m\002"

## Paths.
VENV_PATH="/opt/web-lgsm"
CONNECTOR_PATH="/usr/local/bin"
SHARE_PATH="/usr/local/share/web-lgsm"
PLAYBOOKS_PATH="$SHARE_PATH/playbooks"
SCRIPTPATH=$(cat "$SHARE_PATH/install_conf.json" | jq -r '.APP_PATH')
USERNAME=$(cat "$SHARE_PATH/install_conf.json" | jq -r '.USERNAME')
APT_REQS="$SCRIPTPATH/apt-reqs.txt"

if [[ -z $SCRIPTPATH ]] || [[ -z $USERNAME ]]; then
    echo -e "${RED}Problem parsing $SHARE_PATH/install_conf.json!${RESET}" >&2
    exit 9
fi

cd $SCRIPTPATH
mkdir -p $PLAYBOOKS_PATH
touch "$SHARE_PATH/web-lgsm_custom_users.yml"

# Could break system python if pip is run as root.
if [[ "$EUID" -ne 0 ]]; then
    echo -e "${RED}Run this script as root!${RESET}" >&2
    exit 1
fi

if [[ $(uname) != "Linux" ]]; then
    echo -e "${RED}Only run install script on Debian or Ubuntu Linux!" >&2
    exit 3
fi

if [[ ! -f '/etc/os-release' ]]; then
    echo -e "${RED}No /etc/os-release file found!${RESET}" >&2
    echo -e "${RED}Only run install script on Debian or Ubuntu Linux!${RESET}" >&2
    exit 3
fi

SYS_NAME=$(grep -w 'NAME' /etc/os-release|cut -d= -f2|tr -d '"')

if [[ ! $SYS_NAME =~ Ubuntu|Debian ]]; then
    echo -e "${RED}Install Script Only Supports Debian & Ubuntu Linux!${RESET}" >&2
    echo -e "${YELLOW}See Readme.md for more info.${RESET}"
    exit 3
fi

echo -e "${GREEN}####### Pulling in apt updates...${RESET}"
apt-get update

# Needs curl to get lgsm apt reqs.
if ! which curl &>/dev/null; then
    echo -e "${GREEN}####### Installing \`curl\`...${RESET}"
    apt-get install -y curl
fi

# Function to detect the Ubuntu or Debian version.
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

all_reqs_csv=$(grep 'all,' <<< "$apt_csv" | sed 's/all,//g')
all_reqs=$(tr ',' "\n" <<< "$all_reqs_csv")

# Append lgsm requirements to web-lgsm apt reqs.
echo "$all_reqs" >> "$APT_REQS"

# Install apt requirements!
for req in $(cat "$APT_REQS"); do
    if ! dpkg-query -W --showformat='${db:Status-Status}\n' "$req" 2>/dev/null | grep -q '^installed$'; then
        echo -e "${GREEN}####### Installing \`$req\`...${RESET}"
        echo $req >> installed.log
        apt-get install -y $req
    fi
done

if ! which python3  &>/dev/null; then
    echo -e "${GREEN}####### Installing \`python3\`...${RESET}"
    echo "python3" >> installed.log
    apt-get install -y python3
fi

if ! which pip3 &>/dev/null; then
    echo -e "${GREEN}####### Installing \`pip3\`...${RESET}"
    echo "python3-pip" >> installed.log
    apt-get install -y python3-pip
fi

echo -e "${GREEN}####### Setting up Virtual Env...${RESET}"
python3 -m venv $VENV_PATH

if [[ $SYS_NAME =~ Ubuntu ]]; then
    echo -e "${GREEN}####### Upgrading \`pip3\`...${RESET}"
    $VENV_PATH/bin/python3 -m pip install --upgrade pip
fi

echo -e "${GREEN}####### Installing Python Requirements...${RESET}"
$VENV_PATH/bin/python3 -m pip install -r requirements.txt

## Install Ansible Connector & Playbook files.
echo -e "${GREEN}####### Installing Web-LGSM Ansible Connector...${RESET}"

# First hardcode web-lgsm system user into accepted_users validation list and
# web_user ansible vars files.
echo "  - $USERNAME" >> $SCRIPTPATH/playbooks/vars/accepted_usernames.yml
echo "web_lgsm_user: $USERNAME" > $SCRIPTPATH/playbooks/vars/web_lgsm_user.yml

# Then copy those files into system dirs.
cp -r playbooks/* $PLAYBOOKS_PATH
mv $PLAYBOOKS_PATH/ansible_connector.py $CONNECTOR_PATH

echo -e "${GREEN}####### Setting up Share Modules Dir...${RESET}"

venv_utils="$VENV_PATH/utils"
mkdir "$venv_utils"
cp -r "$SCRIPTPATH/app/utils/shared" "$venv_utils/"

echo -e "${GREEN}####### Setting up Sudoers Rules...${RESET}"

apb="$VENV_PATH/bin/ansible-playbook"
venv_python="$VENV_PATH/bin/python"
ansible_connector="$CONNECTOR_PATH/ansible_connector.py"
accpt_usernames="$PLAYBOOKS_PATH/vars/accepted_usernames.yml"
web_lgsm_user_vars="$PLAYBOOKS_PATH/vars/web_lgsm_user.yml"
sudoers_file="/etc/sudoers.d/$USERNAME-$USERNAME"

# Write sudoers rule for passwordless install & delete.
sudoers_rule="$USERNAME ALL=(root) NOPASSWD: $venv_python $ansible_connector *"
temp_sudoers=$(mktemp)
echo "$sudoers_rule" > "$temp_sudoers"
chmod 0440 "$temp_sudoers"
chown root:root "$temp_sudoers"
visudo -cf "$temp_sudoers"  # Validate new file.
mv "$temp_sudoers" "$sudoers_file"

# Lock playbook files down for security reasons.
find $PLAYBOOKS_PATH -type f -exec chmod 644 {} \;
find $PLAYBOOKS_PATH -type d -exec chmod 755 {} \;
chmod 755 $apb $ansible_connector

echo -e "${GREEN}####### Root Components Successfully Installed!${RESET}"
