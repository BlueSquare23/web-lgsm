# How to Update the Web LGSM

There are two different ways to check for and update the web-lgsm. Users can
update the app either through the web interface. Or via the `web-lgsm.py` cli
script. Using one of these methods rather than `git pull` is preferable because
it will preserve and backup the users existing `main.conf` file.

From within the web interface, on the *Settings* page, you'll find a checkbox
for "Check for and update the Web LGSM!". If you check this box and then click
apply, the web-lgsm will check for and download / apply any necessary updates
via git.

![Settings Page](images/settings_page.png)

Alternatively, CLI users can run the update script directly by cd'ing to the
web-lgsm directory and then running, `./web-lgsm.py --update`. The `web-lgsm.py`
script supports a few options related to updating. You can either check only
with the --check flag, auto update with the --auto flag, or run the regular
update and be prompted with the --update flag.

```
      -u, --update      Update web-lgsm version
      -c, --check       Check if an update is available
      -a, --auto        Run an auto update
```

You can also use this script on a cronjob to enable auto updates for the
project if you would like. More info about that can be found in the [How to
Enable Auto Updates](how_to_enable_auto_updates.md) doc on the subject.

## Updating the Database

The database changed slightly with the release of v1.6. If you've just updated
to v1.6 (or greater) from v1.5 (or below) you can run the `update-db.sh` script
to update your database to be compatible with v1.6.

