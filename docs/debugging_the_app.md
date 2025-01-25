# Debugging the Web LGSM

If you encounter an issue installing, starting, or using the app try these
things:

## Installation Issues

If you're having trouble running the install script you can try the following.

#### Option 1) Run the install script in debug mode and inspect the results

The `install.sh` script supports a `-d` debug mode flag that will enable some
extra output printing to help debug common issues. Simply run `./install.sh -d`
to print the debug output and then look through it for common errors.

You can also either open a github issue and put in your debug output in it or
[contact me directly](https://johnlradford.io/contact.php) and Email me the
output (my contact form will probably mangle the formatting so direct Email is
best). I can look through it and try to help you get the project online!

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
install the python packages within a virtual environment (venv). For non-debug
purposes its recommend to install the required pip reqs in a venv under the
web-lgsm dir.

## Troubleshooting / Debugging

### Debug Config Options

In the `main.conf` file there's a section for `[debug]` that holds some
debugging options. If you encounter a problem with the app, set `debug` to
"true" and `log_level` to "debug" to make the Web-LGSM log everything.

See `config_options.md` (Debug Settings) section, for more info about debug
settings.

### Starting the Web-LGSM in Debug Mode

You can start the web-lgsm in debug mode in your terminal by running:

```
web-lgsm.py --debug
```

For example:

```
» ./web-lgsm.py -d
 [*] Sourcing venv!
 * Root logger level: DEBUG
 * Database Loaded!
 * Serving Flask app 'app'
 * Debug mode: on
[2024-11-29 19:05:44,194] INFO in _internal: WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://45.33.77.9:5000
[2024-11-29 19:05:44,195] INFO in _internal: Press CTRL+C to quit
[2024-11-29 19:05:44,196] INFO in _internal:  * Restarting with stat
 * Root logger level: DEBUG
 * Database Loaded!
[2024-11-29 19:05:45,270] WARNING in _internal:  * Debugger is active!
[2024-11-29 19:05:45,272] INFO in _internal:  * Debugger PIN: ***-***-***
...
```

That will bypass Gunicorn and use Flask's builtin debug web server. Please note,
running the app this way is only recommended for debugging / troubleshooting
purposes. For "production" deployments always use `web-lgsm.py --start`.

### Debug Logging

If you have the `debug` option set to "true" in your main.conf then the app
will log messages at your desired log level to the `logs/error.log` file.

```
logs/error.log
```

## Feel Free to Reach Out!

If you're having trouble using the app or think you've found a bug, please
reach out! You can either open a new Github issue for the project or [contact
me directly](https://johnlradford.io/contact.php). I'll try to get back to you
in a reasonable amount of time!

