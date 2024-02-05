#!/usr/bin/env bash
# Wraps pytest to setup testing env.

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Change dir context in case invoked from outside of web-lgsm dir.
cd "$SCRIPTPATH/.."

set -e

export HOME=$(pwd)
export USERNAME='test'
export PASSWORD='**Testing12345'
export APP_PATH=$(pwd)
export TEST_SERVER='Mockcraft'
export TEST_SERVER_PATH="tests/test_data/Mockcraft"
export CFG_DIR="tests/test_data/Mockraft/lgsm/config-lgsm/mcserver"
export CFG_PATH="tests/test_data/Mockcraft/lgsm/config-lgsm/mcserver/common.cfg"
export TEST_SERVER_NAME='mcserver'
export VERSION='1.3'

# Source virtural env.
if [[ -z "$VIRTUAL_ENV" ]]; then
    source venv/bin/activate
fi

if [[ -f 'app/database.db' ]]; then
    rm 'app/database.db'
fi

## If there's no Mockcraft dir then setup dummy Mockcraft install.
if ! [[ -d "tests/test_data/Mockcraft" ]]; then
    mkdir -p "tests/test_data/Mockcraft/lgsm/config-lgsm/mcserver/"
    cd "tests/test_data/Mockcraft"
    wget -O linuxgsm.sh https://linuxgsm.sh && chmod +x linuxgsm.sh && ./linuxgsm.sh mcserver
    cd "$SCRIPTPATH/.."
fi

# Reset test server cfg.
cp tests/test_data/common.cfg tests/test_data/Mockcraft/lgsm/config-lgsm/mcserver/

# Full test mode vs short test mode for git pre-commit hook.
if [[ $1 =~ '-f' ]]; then
    if ! echo fart|sudo -l -S 2>/dev/null|grep -q tty_tickets; then
        echo "Must have an active sudo tty ticket or can't run in full mode!"
        exit 1
    fi
    # Cleanup any old installs.
    if [[ -d Minecraft ]]; then
        rm -rf Minecraft
    fi
    python -m pytest -v --maxfail=1
else
    python -m pytest -v -k 'not test_full_game_server_install and not test_game_server_start_stop and not test_console_output' --maxfail=1
fi

