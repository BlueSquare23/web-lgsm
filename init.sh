#!/usr/bin/env bash
# This script loads the python environment and starts the gunicorn server.
# Written by John R., April 2023.

PORT=12357
HOST="127.0.0.1"

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Change dir context in case invoked from outside of web-lgsm dir.
cd "$SCRIPTPATH"

# Kindly does the snipping.
function snip(){
    killall gunicorn &>/dev/null &&
        echo "Server Killed!" ||
        echo "Server Not Running."
}

function check_status(){
    if ps aux | grep gunicorn | grep -q web-lgsm; then
        echo "Server Already Running!"
    else
        echo "Server Not Running."
    fi
}

function help(){
    cat <<'    EOF'

    Usage: init.sh [options]

      help|h          Prints this help menu
      start|st        Starts the server (default no args)
      stop|sp         Stop the server
      restart|r       Restart the server
      status|m        Show server status

    EOF
    exit
}

function start_server(){
    # Don't start the server if its already running.
    if check_status | grep Already; then
        exit
    fi
    
    # Print server banner.
    cat <<EOF

        Welcome to the Web LGSM!

    You can access the web-lgsm via the url below!

        http://$HOST:$PORT/

    You can kill the web server with:

        ./init.sh kill

    Please Note: It is strongly advisable to firewall off port $PORT to the
    outside world and then proxy this server to a real web server such as
    Apache or Nginx with SSL encryption! See the Readme for more info.

EOF
    
    # Activate virtual environment.
    if [[ -z "$VIRTUAL_ENV" ]]; then
        source "$SCRIPTPATH/venv/bin/activate"
    fi
    
    # Start the Gunicorn server!
    gunicorn --access-logfile "$SCRIPTPATH/web-lgsm.log" \
        --bind="$HOST:$PORT" \
        --daemon \
        --worker-class gevent 'app:main()'
}

[[ $1  =~ ^-?-?(h|help)$ ]] && help
[[ $1  =~ ^-?-?(st|start)$ ]] && start_server && exit
[[ $1  =~ ^-?-?(m|status|show)$ ]] && check_status && exit
[[ $1  =~ ^-?-?(sp|kill|stop|snip)$ ]] && snip && exit
[[ $1  =~ ^-?-?(r|restart|reload)$ ]] && snip && sleep 2 && start_server && exit
[[ -n $1 ]] && help

start_server
