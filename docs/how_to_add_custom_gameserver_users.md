## Custom Game Server Users

By default the app is hardcoded to only allow the creation and editing of
certain pre-defined usernames.

However, you might already have a game server installed under some other
non-standard user (for example, maybe you installed all your game servers under
the username `coolguy42069`). In this case you'll want to edit/create the file
below and add a custom entry for that username.

* `/usr/local/share/web-lgsm_custom_users.yml`
```
custom_usernames:
  - coolguy42069
```

You can create as many custom entries as you'd like, each must be on its own
line prefixed by two spaces and a hyphen, like the example above.

That file will survive updates (uninstalls/reinstalls) so its the place you'll
want to put any user specific customizations.

From then on the app should be able to install and administer game servers
running as any of your custom usernames.

