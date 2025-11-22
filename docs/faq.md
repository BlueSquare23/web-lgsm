# Frequently Asked Questions

1. Question: I forgot my web-lgsm password, how do I reset it?
  - Answer: You can now run `./web-lgsm.py --passwd` to change the web admin
    user password for the web-lgsm. Simply run the script then enter the
    required prompts to update the web login password.
    - Note: Using `./web-lgsm.py --passwd` is the ONLY way to change the main
      admin users password. All other users passwords (even other admin users)
      can be changed from within the web interface by an admin.

2. Question: How do I enable the game server cfg file editor?
  - Answer: The cfg file editor editor can be enabled by setting `cfg_editor`
    to `yes` in the main.conf file.
    - Note 1: The cfg editor is disabled by default for security reasons, for
      more information see, `docs/config_options.md`.
    - Note 2: Version 1.8 does not yet support the cfg editor for game servers
      in stand alone docker containers.

3. Question: How do I enable the game server console commands Send button?
  - Answer: You can enable game server console commands by setting `send_cmd` to
    `yes` in the main.conf file. This will cause a _Send_ button to appear on
    the controls page. Once pressed, you can then enter the command to send to
    the running game server console.
    - Note 1: Similar to the cfg editor, the game server console commands are
      disabled by default out of an abunance of security precausion. For more
      information see, `docs/config_options.md`.
    - Note 2: This is NOT the same thing as sending shell commands to server.
      If you want to do that, use SSH. This option is only for sending game
      server specific console commands to the running tmux session for your
      game server.

5. Question: I just updated to version 1.8.0 (or greater) from v1.7.0 (or below)
   and now my web-lgsm instance wont start. How do I fix this?
  - Answer: The v1.7 `web-lgsm.py --upgrade` function was unfortunately,
    broken/incomplete. To fully upgrade from 1.7->1.8 you need to run --upgrade
    and then rerun the install.sh script and the `scripts/update-db.sh` script.
    That should fully upgrade you to v1.8. Or just re-install from scratch, and
    re-add your game servers to the web interface manually.

6. Question: Why are some of my home page "Installed Servers" status indicators grey?
  - Answer: If a server's status (on/off) cannot be determined, its status
    indicator will be left grey. This will happen if the game server cannot be
    reached over SSH (for remote & non-same user install types) or if the
    docker container can't be reached.

7. Question: Where's the `init.sh` script?
  - Answer: In version 1.7.0 the `init.sh` script was replaced with the all in
    one `web-lgsm.py` script. It now does all of the old things the init script
    did plus lots more! Run `./web-lgsm.py --help` to see all options!

8. Question: Why don't any of my sudo rules work? / Why does the web app say
   _"sudo: a password is required"_?
   - It may be the case that you have `/etc/sudoers.d` disabled or have
     additional entries for your user after the `#includedir /etc/sudoers.d`
     line. If so simply move those directives above the `#includedir` line.
   - As man sudoers states:
>   When multiple entries match for a user, they are applied in order.
>   Where there are multiple matches, the last match is used (which is not
>   necessarily the most specific match).

9. Question: I'm getting this error why trying to install game servers "Failed
   to change ownership of the temporary files Ansible (via chmod nor setfacl)
   needs to create despite connecting as a privileged user. Unprivileged become
   user would be unable to read the file." How do I fix this?
   - Answer: If you're seeing this error, its likely your install.sh never
     completed fully, and the `playbooks/vars/web_lgsm_user.yml` var is either
     still set to the `<PLACEHOLDER>` value or the incorrect web-lgsm system
     user.
   - To fix this, simply change the username in `playbooks/vars/web_lgsm_user.yml` 
     file to the username the web-lgsm app is running as.

10. Question: How do I reset my 2fa codes?
    - Answer: There are two ways to reset TOTP 2fa codes for web interface
      users.
    - Solution 1 (Web): Have an admin user disable two factor for the user on
      the "Edit Users" page, (Click Submit), then re-enable (Click Submit
      again). The user will then be prompted to setup two factor again on next
      login.
    - Solution 2 (CLI): Use the `./web-lgsm.py --reset_totp` script + option to
      completely reset the totp shared secret for a given user. WARNING - this
      will completely invalidate any devices already setup with totp 2fa for
      the given user.

11. Question: I failed my login a few times and now I just get "Access
    denied" when I try to go to the login page. How do I fix?
    - Answer: Restart the gunicorn server with `./web-lgsm.py --restart`, that
      should clear the lockout blocked IP list.

12. Question: I get a 500 when trying to start the server for the first time.
      OR When I start the server with `web-lgsm.py --debug` I get this error:
    `OperationalError sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: user`
    - Answer: Something as probably gone wrong during your install and the 
      sqlite database has not been setup properly. To fix this and finish initializing the database, run the following:
```bash
cd /path/to/web-lgsm
source /opt/web-lgsm/bin/activate
mv app/database.db app/database.db.bak
touch app/database.db
flask --app app:main db upgrade
```

