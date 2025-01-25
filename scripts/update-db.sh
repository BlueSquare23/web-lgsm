#!/usr/bin/env bash
# Updates database to ensure has required fields for v1.8.

set -e
[[ $1 =~ '-d' ]] && set -x

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd "$SCRIPTPATH/../app"

# sqlite3 should get installed by install.sh but just in case.
if ! [[ -e $(which sqlite3) ]]; then
    echo "The sqlite3 cli is required!"
    echo "Install it with your distributions package manager."
    exit
fi

echo "Backing up existing DB..."
cp database.db database.db.bak

mig_schema_sql=$(cat <<'EOF'
-- Add new columns to `user`
ALTER TABLE user ADD COLUMN role VARCHAR(150);
ALTER TABLE user ADD COLUMN permissions VARCHAR(600);
ALTER TABLE user ADD COLUMN date_created DATETIME;

-- Add new columns to `game_server`
ALTER TABLE game_server ADD COLUMN is_container BOOLEAN;
ALTER TABLE game_server ADD COLUMN install_type VARCHAR(150);
ALTER TABLE game_server ADD COLUMN install_host VARCHAR(150);
ALTER TABLE game_server ADD COLUMN install_finished BOOLEAN;
ALTER TABLE game_server ADD COLUMN keyfile_path VARCHAR(150);

-- Drop the `meta_data` table
DROP TABLE IF EXISTS meta_data;

-- Populate default values
UPDATE user SET role = 'admin', permissions = '{}', date_created = CURRENT_TIMESTAMP;
UPDATE game_server SET is_container = 0, install_type = 'local', install_host = 'localhost', install_finished = 1, keyfile_path = '';
EOF
)

sqlite3 database.db <<< $mig_schema_sql

echo "Database Update Completed!"
