#!/usr/bin/env bash
# Web-LGSM Install script. Installs required software dependencies and
# configures environment for web-lgsm application.
# Written by John R., April 2023. Re-written August 2025.

# Strict mode, close on any non-zero exit status.
set -eo pipefail

## Globals

# Colors!
RED="\001\e[31m\002"
GREEN="\001\e[32m\002"
YELLOW="\001\e[33m\002"
RESET="\001\e[0m\002"

# Paths.
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
VENV_PATH="/opt/web-lgsm"
CONNECTOR_PATH="/usr/local/bin"
SHARE_PATH="/usr/local/share/web-lgsm"
PLAYBOOKS_PATH="$SHARE_PATH/playbooks"

# Options.
declare -A OPT=(
    [skiproot]=false
    [debug]=false
)

# Preflight checks.
if [[ "$EUID" -eq 0 ]]; then
    echo -e "${RED}Do NOT run this script as root!${RESET}" >&2
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
    echo -e "${RED}Install Script Only Supports Debian & Ubuntu Linux!${RESET}"
    echo -e "${YELLOW}See Readme.md for more info.${RESET}"
    exit 3
fi

function usage() {
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -h, --help        Show this help message"
    echo "  -d, --debug       Run in debug mode (aka set -x)"
    echo "  -s, --skiproot    Don't install root components (for headless updates)"
    echo "  -c, --docker      Install & setup docker system components"
    echo
    exit 0
}

function run_install() {
    # In case script is invoked outside of web-lgsm dir.
    cd $SCRIPTPATH

    # Skip root setup for unattended upgrades.
    if [[ "${OPT[skiproot]}" == false ]]; then
        sudo -v
        sudo mkdir -p $PLAYBOOKS_PATH
        
        # Build install conf.
        cat << EOF | sudo tee "$SHARE_PATH/install_conf.json" >/dev/null
{
  "USERNAME": "$USER",
  "APP_PATH": "$SCRIPTPATH"
}
EOF
        # Enable debug on root_install.sh
        [[ "${OPT[debug]}" == true ]] && debug="-d"

        sudo mkdir -p "$VENV_PATH/bin/"
        sudo cp scripts/root_install.sh scripts/update.py uninstall.sh "$VENV_PATH/bin/"
        sudo chmod 750 "$VENV_PATH/bin/root_install.sh" "$VENV_PATH/bin/uninstall.sh"  "$VENV_PATH/bin/update.py"
        sudo $VENV_PATH/bin/root_install.sh "$debug"
    fi

    echo -e "${GREEN}####### Installing NPM Requirements...${RESET}"
    cd $SCRIPTPATH/app/static/js
    npm install @xterm/xterm
    npm install --save @xterm/addon-fit
    cd $SCRIPTPATH

    # Finally setup random key.
    random_key=$(echo $RANDOM | md5sum | head -c 20)
    echo "SECRET_KEY=\"$random_key\"" > .secret
    chmod 600 .secret

    echo -e "${GREEN}####### Updating Database...${RESET}"
    /opt/web-lgsm/bin/flask --app app:main db upgrade

    echo -e "${GREEN}####### Project Setup & Installation Complete!!!${RESET}"
    echo -e "${GREEN}Run the \`web-lgsm.py\` script to start the server.${RESET}"
}

function install_docker() {
    # Literally just stealing the install from the docker docs.
    # https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
    echo -e "${GREEN}####### Install Apt Docker Components...${RESET}"

    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings

    arch=$(dpkg --print-architecture)
    codename=$(. /etc/os-release && echo "$VERSION_CODENAME")
    pkg_url=''

    if [[ $SYS_NAME =~ Ubuntu ]]; then
        # Add Docker's official GPG key:
        sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
        sudo chmod a+r /etc/apt/keyrings/docker.asc
        
        pkg_url='https://download.docker.com/linux/ubuntu'
    else
        # Else do Debian install.
        sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
        sudo chmod a+r /etc/apt/keyrings/docker.asc
        pkg_url="https://download.docker.com/linux/debian"
    fi

    # Add the repository to Apt sources:
    echo "deb [arch=$arch signed-by=/etc/apt/keyrings/docker.asc] $pkg_url $codename stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    echo -e "${GREEN}####### Docker install completed successfully!${RESET}"
    printf "Run: ./docker-setup.py --add\n  to add your game server port and build docker confs\n"
    exit
}

# Main.
function main() {
    # Parse command line options.
    local TEMP
    TEMP=$(getopt -o hdsc --long help,debug,skiproot,docker -n "$0" -- "$@")
    
    if [ $? != 0 ]; then
        echo "Error in command line arguments" >&2
        usage
    fi
    
    eval set -- "$TEMP"
    
    # Extract options and their arguments.
    while true; do
        case "$1" in
            -h|--help)
                usage
                ;;
            -c|--docker)
                install_docker
                break
                ;;
            -d|--debug)
                set -x
                echo $EUID
                ls -lah
                printenv
                OPT[debug]=true
                run_install
                break
                ;;
            -s|--skiproot)
                OPT[skiproot]=true
                run_install
                break
                ;;
            --)
                run_install
                break
                ;;
            *)
                echo "Internal error!" >&2
                exit 1
                ;;
        esac
    done
}

main "$@"

