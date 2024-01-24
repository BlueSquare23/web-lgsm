# Debugging the Web LGSM

If you encounter an issue installing, starting, or using the app try these
things:

## Installation Issues

If you're having trouble running the install script you can try the following.

#### Option 1) Run the install script in debug mode and inspect the results

The `install.sh` script supports a `-d` debug mode flag that will enable some
extra output prining to help debug common issues. Simply run `./install.sh -d`
to print the debug output and then look through it for common errors.

You can also either open a github issue and put in your debug output in it or
[contact me directly](https://johnlradford.io/contact) and Email me the output
(my contact form will probably mangle the formatting so direct Email is best).
I can look through it and try to help you get the project online!

#### Option 2) Manually install the required apt and python packages

The required apt packages are listed in `apt-reqs.txt` file. If you run the
command below it should manually install them.

```
sudo apt update && sudo apt install -y tmux curl watch wget findutils
```

From there you'll just have to install the required python packages. The
required python packages are stored in a file called `requirements.txt`. You
can do this with python's `pip` package manager.

```
pip3 install -r requirements.txt
```

Please note, the command above will install the python packages as your system
user (aka in ~/.local/bin/). Whereas, by default the web-lgsm will try to
install the python packages within a virtual environment (venv).

## Trouble Starting the Web LGSM

If you're having trouble starting the app with the `init.sh` script or having
trouble with some feature of the app, then you can investigate further by
starting the app in debug mode in your terminal. To do so simply ssh to the
server, cd to the web-lgsm installation directory, and then run: 
`./scripts/debug.py`.

```
» ./scripts/debug.py
 * Created Database!
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://45.33.77.9:5000
Press CTRL+C to quit
 * Restarting with stat
 * Created Database!
 * Debugger is active!
 * Debugger PIN: ***-***-***
```

That will bypass Gunicorn and use Flask's builtin debug web server. Please note,
running the app this way is only recommended for debugging / troubleshooting
purposes. For production deployments always use the `init.sh` script.

## Feel Free to Reach Out!

If you're having trouble using the app or think you've found a bug, please
reach out! You can either open a new Github issue for the project or [contact
me directly](https://johnlradford.io/contact). I'll try to get back to you in a
reasonable amount of time!

