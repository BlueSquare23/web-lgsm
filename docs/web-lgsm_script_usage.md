# Managing the Web LGSM via the web-lgsm.py Script

You can use the `web-lgsm.py` script in the project's main directory to manage
the web-lgsm itself (aka stop, start, restart, check status).

That script supports a number of optional arguments. If you ever need to see
them you can run `web-lgsm.py -h` to see them.

```
» ./web-lgsm.py --help

    Usage: web-lgsm.py [options]

      Options:

      -h, --help        Prints this help menu
      -s, --start       Starts the server (default no args)
      -q, --stop        Stop the server
      -r, --restart     Restart the server
      -m, --status      Show server status

```

As the help menu mentions, if you run `web-lgsm.py` with no args it will
attempt to start the server.
