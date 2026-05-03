# File Manager

The Web LGSM includes a builtin file manager that is disabled by default.

> "Why is it disabled by default?"

Well because having a web portal that allows arbitrary file browsing, editing,
uploading, downloading, etc. could be considered a huge f\*cking security hole.

So we want to ship the most secure version of the app we can out of the box and
then mark this feature _"use at your own risk!"_

## Enabling the File Manager

To enable the file manager, set `file_manager = yes` in your main.conf (or
main.conf.local) file.

You can then access the file manager by going to the `/files` page.

## File Manager Permissions & Scope

The file manager is not able to access any files outside of one of the game
server users home directories. So you can't edit system files with it.

Likewise if your web-lgsm web portal user doesn't have access to some game
server (as some system user), then you cannot edit files for that game server
system user.

For example, say your admin has Minecraft installed as the `mcserver` user and
Multi Theft Auto installed as the `mtaserver` user. If you only have web-lgsm
access to the Minecraft server, you cannot edit files for the Minecraft server.

Similarly, any non-admin users can be give "read only" access to the file
manager, allowing them to view and browse files, but not edit, upload, or
delete them.

## Custom Excludes

If you'd like to lock down the file manager even further, you can create a
custom exclude file here:

```
/usr/local/share/web-lgsm_exclude.yml
# sudo chown root:root
# sudo chmod 664 
```

**Formatted like this:**

```yaml
exclude_files:
  - file123.txt
  - "*.sh"

exclude_dirs:
  - /home/user123/some/path
  - /home/user456/another_path
```

The custom excludes support globs (not full blow regex, just `*`).

Anything matching one of the excluded file names or under one of the excluded
directory paths will be off limits to the file manager.

