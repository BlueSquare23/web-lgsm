#!/usr/bin/env bash
# Wraps pytest to setup testing env.

set -e

# Source virtural env.
if [[ -z "$VIRTUAL_ENV" ]]; then
    source venv/bin/activate
fi

if [[ -f 'app/database.db' ]]; then
    rm 'app/database.db'
fi

# If there's no Minecraft dir then setup dummy Minecraft install.
if ! [[ -d Minecraft ]]; then
    mkdir -p Minecraft/lgsm/config-lgsm/mcserver/
    cd Minecraft
    wget -O linuxgsm.sh https://linuxgsm.sh && chmod +x linuxgsm.sh && ./linuxgsm.sh mcserver
    cd ..
fi
# Reset test server cfg.
cp tests/test_data/common.cfg Minecraft/lgsm/config-lgsm/mcserver/

python -m pytest -v 
