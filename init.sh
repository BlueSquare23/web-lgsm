#!/usr/bin/env bash
# This script uses the built in python web server in order to serve the cgi
# application.
# Written by John R., Feb. 2023.

PORT="8080"

function cleanup(){
    pid=$(ps aux|grep python|grep "http.server"|awk '{print $2}')
    kill -9 $pid 2> /dev/null || echo "Web server not running."
    exit
}

if [[ "$1" == "kill" ]]; then
    cleanup
fi

# Check if in correct dir.
if [[ $(basename $(pwd)) != "web-lgsm" ]]; then
    echo "Script must be run from web-lgsm directory!"
    exit 2
fi

# Source venv if not already sourced.
if [[ -z $VIRTUAL_ENV ]]; then
    source venv/bin/activate
fi

# Print usage.
cat << EOF

You can access the web-lgsm via the url below!

  http://`hostname`:$PORT/

Start the web server in the background,

  ./init.sh bg

To kill the web server,

  ./init.sh kill

EOF

if [[ "$1" == "bg" ]]; then
    python3 -m http.server $PORT --cgi &> httpd.log &
else
    python3 -m http.server $PORT --cgi
fi

