#!/usr/bin/env bash
# This install script downloads python3 and pip3 if necessary, it also sets up
# the project's python virtualenv and installs the necessary python modules.
# Written by John R., April 2023.

# Strict mode, close on any non-zero exit status.
set -eo pipefail

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
    echo -e "${red}Only run on Ubuntu Linux!"
    exit 3
fi

if [[ ! -f '/etc/os-release' ]]; then
    echo -e "${red}No /etc/os-release file found!${reset}"
    echo -e "${red}Only run on Ubuntu Linux!${reset}"
    exit 3
fi

sys_name=$(grep -w 'NAME' /etc/os-release|cut -d= -f2|tr -d '"')

if [[ ! $sys_name =~ Ubuntu|Debian ]]; then
    echo -e "${red}Only Supported on Debian & Ubuntu Linux!${reset}"
    exit 3
fi

echo -e "${green}####### Pulling in apt updates...${reset}"
sudo apt update

for req in $(cat 'apt-reqs.txt'); do
    if ! which $req &>/dev/null; then
        echo -e "${green}####### Installing \`$req\`...${reset}"
        sudo apt install -y $req
    fi
done

if ! which python3  &>/dev/null; then
    echo -e "${green}####### Installing \`python3\`...${reset}"
    sudo apt install -y python3
fi

if ! which pip3 &>/dev/null; then
    echo -e "${green}####### Installing \`pip3\`...${reset}"
    sudo apt install -y python3-pip

    if [[ $sys_name =~ Ubuntu ]]; then
        echo -e "${green}####### Upgrading \`pip3\`...${reset}"
        python3 -m pip install --upgrade pip
    fi
fi

if ! python3 -c "import virtualenv"; then
    if [[ $sys_name =~ Ubuntu ]]; then
        echo -e "${green}####### Installing \`virtualenv\`...${reset}"
        python3 -m pip install --user virtualenv
    fi

    if [[ $sys_name =~ Debian ]]; then
        sudo apt install -y python3-venv
    fi
fi

echo -e "${green}####### Setting up Virtual Env...${reset}"
if [[ $sys_name =~ Ubuntu ]]; then
    python3 -m virtualenv venv
fi
if [[ $sys_name =~ Debian ]]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo -e "${green}####### Install Requirements...${reset}"
python3 -m pip install -r requirements.txt

random_key=$(echo $RANDOM | md5sum | head -c 20)
echo "SECRET_KEY=\"$random_key\"" > .secret
chmod 600 .secret

echo -e "${green}####### Project Setup & Installation Complete!!!${reset}"
echo -e "${green}Run the \`init.sh\` to start the server.${reset}"

