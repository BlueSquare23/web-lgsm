# How to Setup the Web LGSM as a Systemd Service

## Run Systemd Setup Script

You can use the `setup_systemd_service.sh` script to configure the web-lgsm as
a local user systemd service.

Change dirs to the web-lgsm dir:

```
cd /path/to/web-lgsm
```

Then run the script:
```
./scripts/setup_systemd_service.sh
```

Using systemd to manage the app will ensure the web-lgsm is automatically
started on system startup and means you can use the `systemctl --user` command
to stop, start, and restart the web-lgsm app from there on out.

## How to Stop, Start, Restart Web LGSM via Systemctl

Start the web-lgsm:

```
systemctl --user start web-lgsm
```

Stop the web-lgsm:

```
systemctl --user stop web-lgsm
```

Check status:

```
systemctl --user status web-lgsm
```

