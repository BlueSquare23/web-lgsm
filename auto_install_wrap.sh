#!/usr/bin/env bash
# This is a web-lgsm helper script which wraps the auto install process. This
# script mainly exists to copy the lgsm _default.cfg file for a given game
# server to a common.cfg file the auto installation completes. 

if [[ -z $1 ]]; then
    /usr/bin/echo "Missing Required Arg!"
    exit
fi

lgsm_script="$1"

# Attempt at basic sanitization.
bad_chars='\$ \" \\ \# \= \[ \] \! \< \> \| \; \{ \} \( \) \* \, \? \~ \&'
for char in $bad_chars; do
    lgsm_script=$(/usr/bin/tr -d "$char" <<< $lgsm_script)
done

# Check that first arg is in game_servers.json.
if ! /usr/bin/grep -wq "$lgsm_script" ../json/game_servers.json 2>/dev/null; then
    /usr/bin/echo "Invalid Script Arg!"
    exit
fi

# Run the auto install.
./${lgsm_script} auto-install

# Find the default and common configs.
default_cfg=$(/usr/bin/find "lgsm/config-lgsm" -name "_default.cfg")
common_cfg=$(/usr/bin/find "lgsm/config-lgsm" -name "common.cfg")

# Strip the first 9 lines of warning comments from _default.cfg and write the
# rest to the common.cfg.
/usr/bin/tail -n +9 "$default_cfg" > "$common_cfg"

/usr/bin/echo "Default game server config copied to common.cfg!"
