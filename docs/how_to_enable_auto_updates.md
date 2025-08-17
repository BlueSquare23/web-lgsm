# How to Enable Automatic Updates

Create a new root crontab entry like the one below to enable auto updates for
this project.

Will run at 02:30 AM on Sundays.

```
30 2 * * 0  /opt/web-lgsm/bin/update.py --quiet --auto
```

The update mechanism needs to run as root in order install apt packages and
setup other system level components non-interactively.

## More Info on Using Cron on Linux

[Cronjobs in Linux - FreeCodeCamp](https://www.freecodecamp.org/news/cron-jobs-in-linux/)

[Linux, Unix, macOS Cron Jobs - Engineer Man](https://www.youtube.com/watch?v=QEdHAwHfGPc)

