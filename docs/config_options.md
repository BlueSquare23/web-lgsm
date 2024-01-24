# Web LGSM Configuration Options

The configuration file for the web-lgsm is named `main.conf` and lives in the
project's root directory. This file contains the configurable parameters for
this app. When the user updates something through the `/settings` page of the
app its value is stored in the main.conf file. However, not all values in the
`main.conf` are configurable through the settings page (for security reasons,
see `cfg_editor`).

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

### General Settings

These settings control basic app behaviors.

* `remove_files`: Controls whether game server files are deleted or not
  whenever a game server entry is removed from the web-lgsm.
  - Default: No (aka keep files on game server delete)

* `cfg_editor`: Controls whether the game server cfg file editor is enabled
  or disabled.
  - Default: No (aka cfg file editor disabled)
  - Warning: Enabling this feature has inherent security risks! If you're going
    to enable this just be sure to have a strong password, have SSL, and trust
    who you give web-lgsm access too!

## A Subtle Distinction in Nomenclature

For the purposes of keeping things straight I've tried to stick to calling game
server configuration files *cfg* files (as is the convention used by the folks
at the LGSM) and the main Web LGSM configuration file a *config* file.

You'll notice this distinction used throughout the code, comments, and
documentation.
