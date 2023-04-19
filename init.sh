#!/usr/bin/env bash
# This script loads the python environment and starts the gunicorn server.
# Written by John R., April 2023.

PORT=12357
HOST="127.0.0.1"

# Kindly does the snipping.
function snip(){
    killall gunicorn &>/dev/null &&
        echo "Server Killed!" ||
        echo "Server Not Running."
    exit
}

[[ $1  =~ ^(kill|snip)$ ]] && snip

# Print usage.
cat << EOF

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
    source venv/bin/activate
fi

## Start the Gunicorn server!
# Uses gevent concurrent networking library with gunicorn to allow async
# support so shell subprocs are handled properly. Otherwise, apt dependancy
# installs during auto game server install process fails. More info,
# https://flask.palletsprojects.com/en/2.2.x/deploying/gunicorn/#async-with-gevent-or-eventlet
gunicorn --access-logfile "web-lgsm.log" \
    --workers=4 \
    --bind="$HOST:$PORT" \
    --daemon \
    --worker-class gevent 'app:main()'

