#!/usr/bin/env bash
# Web-LGSM update script.
# Written by John R., Jan. 2024.

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Change dir context in case invoked from outside of web-lgsm dir.
cd "$SCRIPTPATH/.."
if [[ "$@" =~ '-h' ]]; then
    echo "Usage:"
    echo "      update.sh [options]"
    echo
    echo " -h     Print this help menu"
    echo " -a     Auto mode, no prompts"
    exit
fi

# Check for updates.
git remote update
UPSTREAM='@{u}'
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

if [ $LOCAL = $REMOTE ]; then
    echo "Already Up-to-date!"
elif [ $LOCAL = $BASE ]; then
    echo "Update Required!"
    if ! [[ "$@" =~ '-a' ]]; then
        echo -n "Would you like to update now? (y/n): "
        read resp
        if ! [[ $resp =~ y ]]; then
            exit
        fi

        # Check for modified files and warn.
        modified=$(git status|grep modified|awk '{print $2}'|grep -Ev '.secret|main.conf')
        if [[ -n $modified ]]; then
            echo "!!! The following files have been modified and will be overwritten by an update !!!"
            for file in $modified; do
                echo "    Modified: $file"
            done
            echo -n "Are you sure you want to continue? (y/n): "
            read resp
            if ! [[ $resp =~ y ]]; then
                exit
            fi
        fi
    fi

    # Backup main.conf file.
    epoc=$(date +"%s")
    conf="main.conf"
    cp $conf $conf.$epoc.bak
    # Git restore anything that needs it.
    git restore $conf
    for file in $modified; do
        git restore $file
    done
    # Git pull.
    git pull
    # Manually diff and path main.conf.
    # This way user keeps their settings but get's new updates.
    diff -u $conf $conf.$epoc.bak > $conf.path
    patch $conf $conf.path
fi

