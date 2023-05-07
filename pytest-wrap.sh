#!/usr/bin/env bash
# Wraps pytest to setup testing env.

set -e

# Source virtural env.
if [[ -z "$VIRTUAL_ENV" ]]; then
    source venv/bin/activate
fi

# Check if GITHUB_WORKSPACE var set (aka is gh actions test runner).
if [[ -z "$GITHUB_WORKSPACE" ]]; then
    GITHUB_WORKSPACE="."
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

python -m pytest -v 
