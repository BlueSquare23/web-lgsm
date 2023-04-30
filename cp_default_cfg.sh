#!/usr/bin/env bash
# This is a web-lgsm helper script to copy the lgsm _default.cfg file for a
# given game server to a common.cfg file as part of the post install config
# setup.

default_cfg=$(/usr/bin/find "lgsm/config-lgsm" -name "_default.cfg")

common_cfg=$(/usr/bin/find "lgsm/config-lgsm" -name "common.cfg")

# Strip the first 9 lines of warning comments from _default.cfg.
/usr/bin/tail -n +9 "$default_cfg" > "$common_cfg"

/usr/bin/echo "Default game server config copied to common.cfg!"
