# Web LGSM Configuration Options

The configuration file for the web-lgsm is named `main.conf` and lives in the
project's root directory. This file contains the configurable parameters for
this app. When the user updates something through the `/settings` page of the
app its value is stored in the main.conf file. However, not all values in the
`main.conf` are configurable through the settings page (for security reasons,
see `cfg_editor`).

Users can also copy the `main.conf` file to `main.conf.local` to create a
version of the file that will not be touched by updates. If a `main.conf.local`
file exists in the main web-lgsm directory, its configuration parameters will
override anything set in the `main.conf` file.

These config parameters are stored in an INI style format and parsed using the
Python `configparser` library.

## Current Config Parameters

### Aesthetic

These parameters control something about the way the app looks.

* `text_color`: Controls the color of the terminal console output for the
  install & controls pages.

* `text_area_height`: Controls the default line number height of the output
  text area for the install & controls pages.
  - Default: 10

* `graphs_primary`: Controls the color of the %Used for the stats graphs.

* `graphs_secondary`: Controls the color of the %Free for the stats graphs.

* `show_stats`: Controls whether or not to show the Game Server Stats. The
  stats and graphs are cool but they do generate a lot of requests to the web
  server. If someone doesn't want to use them I wanted to make it easy to turn
  them off.
  - Default: Yes

* `show_barrel_roll`: Controls whether or not to show the "Do a Barrel Roll"
  button. Hidden feature, just for you if you're reading this. Set it to yes
  and then click do a barrel roll on the home page!
  - Default: Hidden Feature


### General Settings

These settings control basic app behaviors.

* `remove_files`: Controls whether game server files are deleted or not
  whenever a game server entry is removed from the web-lgsm.
  - Default: No (aka keep files on game server delete)

* `cfg_editor`: Controls whether the game server cfg file editor is enabled
  or disabled.
  - Default: No (aka cfg file editor disabled)
  - Warning: Enabling this feature has inherent security risks! Certain game
    server cfgs may allow for arbitrary shell code to be inserted and run once
    the game server is started. If you're going to enable this feature just be
    sure to have a strong password, have SSL, and trust who you give web-lgsm
    access too!

* `send_cmd`: Controls if "Send command to running game server console" button
  on /controls page is enabled or disabled.
  - Default: No (aka send button is disabled)
  - Warning: Similarly to the `cfg_editor` option, there are some risks
    associated with enabling the `send_cmd` setting. Certain game server
    consoles may allow arbitray code execution. If you're going to enable this
    feature just be sure to have a strong password, have SSL, and trust who you
    give web-lgsm access too!

* `allow_custom_jobs`: Allows the creation of arbitrary cronjobs via the app's
  builtin jobs editor.
  - Default: No (aka custom cronjobs disabled)
  - Warning: THIS FEATURE ENABLES ARBITRARY REMOTE CODE EXECUTION FOR
    AUTHENTICATED USERS! By enabling custom jobs, you are giving users the
    ability to run any shell commands they want on your system!


### Server Settings

* `host`: The hostname or IP address the gunicorn server will run under. 
  - Default: 127.0.0.1
  - Warning: Unless you have good reason to, don't change this from the
    default. See `docs/suggested_deployment.md` for more info.

* `port`: The port number the gunicorn server will run on.
  - Default: 12357
  - Warning: Unless you have good reason to, don't change this from the
    default. See `docs/suggested_deployment.md` for more info.

* `cert` (optional): Path to SSL certificate `cert.pem` file for Gunicorn server.
  - Default: None

* `key` (optional): Path to SSL certificate `key.pem` file for Gunicorn server.
  - Default: None

### Debug Settings

* `debug` (bool): Controls whether or not server debug logging should be
  enabled. Useful for gather additional debugging information.
  - Default: No

* `log_level`: Controls the type of messages / events that will be logged in
  debug mode.
  - Options:
    - warning: Least verbose. Just log warnings & misc info.
    - info: Mid verbose. Logs general info on app state, variables values, etc.
    - debug: Most verbose. Logs everything all command output everything.
  - Default: info

## A Subtle Distinction in Nomenclature

For the purposes of keeping things straight I've tried to stick to calling game
server configuration files *cfg* files (as is the convention used by the folks
at the LGSM) and the main Web LGSM configuration file a *config* file.

Likewise, I've made a similar distinction between *controls* or *commands* and
*cmds*. When I use the three letter *cmd* I'm referring to a command that is run
via the send button within a running game server console. Whereas, when the
web-lgsm app itself executes a command via a shell process I'm calling that a
*command*.

You'll notice these distinctions used throughout the code, comments, and
documentation.
