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
    echo " -c     check mode, does NOT update"
    exit
fi

# Check for updates.
git remote update
UPSTREAM='@{u}'
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

# For Debug.
#echo $UPSTREAM
#echo $LOCAL
#echo $REMOTE
#echo $BASE
#set -x

if [ $LOCAL = $REMOTE ]; then
    echo "Already Up-to-date!"
    exit
elif [ $LOCAL = $BASE ]; then
    echo "Update Required!"
    [[ "$@" =~ '-c' ]] && exit

    # If not in auto mode, prompt user.
    if ! [[ "$@" =~ '-a' ]]; then
        echo -n "Would you like to update now? (y/n): "
        read resp
        if ! [[ $resp =~ y ]]; then
            exit
        fi

        # Check for modified files and warn.
        modified=$(git status|grep modified|awk '{print $2}'|grep -Ev '.secret')
        if [[ -n $modified ]]; then
            echo "!!! The following files have been modified and will be overwritten by an update !!!"
            echo "The main.conf will be backed up"
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
    echo "Backing up $conf to $conf.$epoc.bak"

    # Git restore anything that needs it.
    for file in $modified; do
        git restore $file
    done

    # Git pull.
    echo "Pulling in new code from github..."
    git pull

    # Update pip modules.
    echo "Backing up venv to venv.$epoc.bak and creating new one"
    mv venv venv.$epoc.bak
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing new pip reqs..."
    python3 -m pip install -r requirements.txt

    echo "Update completed!"
    exit
elif [ $REMOTE = $BASE ]; then
    echo "Local ahead of remote, need push?" >&2
    echo "Note: Normal users should not see this." >&2
    exit 1
fi

# Should never get to this line.
echo "Something has gone horribly wrong!" >&2
echo "Its possible your local repo has diverged." >&2
exit 2
