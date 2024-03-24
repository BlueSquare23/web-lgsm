#!/usr/bin/env bash
# Set's up the web-lgsm as a systemd service so it can be autostarted at boot
# and managed via systemctl.

# Strict mode, close on any non-zero exit status.
set -eo pipefail

# Run as the user the web-lgsm is running as.
if [[ "$EUID" -eq 0 ]]; then
    echo -e "Do NOT run this script as root!"
    exit 1
fi

# In case script is invokes from outside of web-lgsm dir.
SCRIPTPATH="$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P)"
WEBLGSM_DIR="$(cd $SCRIPTPATH/.. && pwd)"

CONFIG_DIR="$HOME/.config/systemd/user/"

# Make local systemd config dir if it doesn't exist.
if ! [[ -d $CONFIG_DIR ]]; then
    mkdir -p $CONFIG_DIR
fi

# Ask before overwrting unit file.
if [[ -f "$CONFIG_DIR/web-lgsm.service" ]]; then
    echo "A unit file for this service already exists!"
    echo -n "Do you want to overwrite this file? (y/n): "
    read answer
    if ! [[ $answer =~ ^(y|Y)$ ]]; then
        echo "Exiting..."
        exit
    fi
fi

# Create new systemd service.
cat <<EOF > "$CONFIG_DIR/web-lgsm.service"
[Unit]
Description="Web LGSM - A Simple Web Interface for the LinuxGSM"

[Service]
Type=forking
WorkingDirectory=/home/steam/web-lgsm
ExecStart=/home/steam/web-lgsm/init.sh
ExecStop=/home/steam/web-lgsm/init.sh stop
Restart=always

[Install]
WantedBy=default.target
EOF

# Enable local systemd services.
loginctl enable-linger $USER

# Check if user has XDG_RUNTIME_DIR set. If not, set it for initial setup then
# yell at the user and tell them to set it manually themselves.
if [[ -z $XDG_RUNTIME_DIR ]]; then
    export XDG_RUNTIME_DIR=/run/user/$UID
cat <<EOF
You'll need to set the following environment variable in your login shell's RC file!
    XDG_RUNTIME_DIR=/run/user/$UID

For Bash/Zsh run this command:
    echo "export XDG_RUNTIME_DIR=/run/user/$UID" >> ~/.bashrc

For Csh/Tcsh run this command:
    echo "setenv XDG_RUNTIME_DIR /run/user/$UID" >> ~/.cshrc
EOF
fi

# Reload and enable the service.
systemctl --user daemon-reload
systemctl --user enable --now web-lgsm
systemctl --user status web-lgsm

cat << EOF
Web LGSM Systemd Service Enabled!

You can now stop/start/restart the server with the commands below.

    systemctl --user stop web-lgsm
    systemctl --user start web-lgsm
    systemctl --user restart web-lgsm
EOF
