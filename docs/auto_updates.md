# Automatic Updates

You can enable automatic updates for this project by adding a cronjob like the
one below to your users crontab.

At 02:30 AM on Sunday.

```
2 30 * * 0  /home/$USER/web-lgsm/scripts/update.sh -a
```

Be sure to replace `/home/$USER/web-lgsm/` with the path to your web-lgsm
installation.

## More Info on Using Cron on Linux

[Cronjobs in Linux - FreeCodeCamp](https://www.freecodecamp.org/news/cron-jobs-in-linux/)

[Linux, Unix, macOS Cron Jobs - Engineer Man](https://www.youtube.com/watch?v=QEdHAwHfGPc)
