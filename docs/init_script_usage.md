# Managing the Web LGSM via the init.sh Script

You can use the `init.sh` script in the project's main directory to manage the
web-lgsm itself (aka stop, start, restart, check status).

That script supports a number of optional arguments. If you ever need to see
them you can run `init.sh -h` to see them.

```
» ./init.sh --help

    Usage: init.sh [options]

      help|h          Prints this help menu
      start|st        Starts the server (default no args)
      stop|sp         Stop the server
      restart|r       Restart the server
      status|m        Show server status
```

As the help menu mentions, if you run `init.sh` with no args it will attempt to
start the server.

I've made it so the init script accepts the same shorthand options (h, st, sp,
r, m) as the LGSM scripts themselves.
