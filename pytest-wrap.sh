#!/usr/bin/env bash
# Wraps pytest to setup testing env.

set -e

if [[ -z "$VIRTUAL_ENV" ]]; then
    source venv/bin/activate
fi

rm app/database.db

# If there's no Minecraft dir then setup dummy Minecraft install.
if ! [[ -d Minecraft ]]; then
    mkdir Minecraft
    cd Minecraft
    wget -O linuxgsm.sh https://linuxgsm.sh && chmod +x linuxgsm.sh && ./linuxgsm.sh mcserver
    cd ..
fi

python -m pytest -v
