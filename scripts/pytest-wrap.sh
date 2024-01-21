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
export TEST_SERVER='Minecraft'
export TEST_SERVER_PATH="tests/test_data/Minecraft"
export CFG_DIR="tests/test_data/Minecraft/lgsm/config-lgsm/mcserver"
export CFG_PATH="tests/test_data/Minecraft/lgsm/config-lgsm/mcserver/common.cfg"
export TEST_SERVER_NAME='mcserver'
export VERSION='1.3'

# Source virtural env.
if [[ -z "$VIRTUAL_ENV" ]]; then
    source venv/bin/activate
fi

if [[ -f 'app/database.db' ]]; then
    rm 'app/database.db'
fi

## If there's no Minecraft dir then setup dummy Minecraft install.
if ! [[ -d "tests/test_data/Minecraft" ]]; then
    mkdir -p "tests/test_data/Minecraft/lgsm/config-lgsm/mcserver/"
    cd "tests/test_data/Minecraft"
    wget -O linuxgsm.sh https://linuxgsm.sh && chmod +x linuxgsm.sh && ./linuxgsm.sh mcserver
    cd ../../..
fi

# Reset test server cfg.
cp tests/test_data/common.cfg tests/test_data/Minecraft/lgsm/config-lgsm/mcserver/

python -m pytest -v --maxfail=1
