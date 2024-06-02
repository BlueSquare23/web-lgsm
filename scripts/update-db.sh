#!/usr/bin/env bash
# Updates database from pre-v1.5 to be compatible with v1.6+.

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd "$SCRIPTPATH/../app"

if ! [[ -e $(which sqlite3) ]]; then
    echo "The sqlite3 cli is required!"
    echo "Install it with your distributions package manager."
    exit
fi

if sqlite3 database.db '.schema game_server' | grep -q username; then
    echo "[*] Database already updated!"
else
    echo "[*] Backing up database to database.db.bak"
    cp database.db database.db.bak
    echo "[*] Adding new username column to game_servers"
    sqlite3 database.db 'ALTER TABLE game_server ADD COLUMN username VARCHAR(150);'
fi
