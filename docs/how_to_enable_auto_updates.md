# How to Enable Automatic Updates

You can enable automatic updates for this project by adding a cronjob like the
one below to your users crontab.

Will run at 02:30 AM on Sundays.

```
2 30 * * 0  /path/to/web-lgsm/web-lgsm.py --auto
```

Be sure to replace `/path/to/web-lgsm/` with the path to your web-lgsm
installation.

## More Info on Using Cron on Linux

[Cronjobs in Linux - FreeCodeCamp](https://www.freecodecamp.org/news/cron-jobs-in-linux/)

[Linux, Unix, macOS Cron Jobs - Engineer Man](https://www.youtube.com/watch?v=QEdHAwHfGPc)
