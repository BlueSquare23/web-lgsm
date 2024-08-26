# Frequently Asked Questions

1. Question: I forgot my web-lgsm password, how do I reset it?
  - Answer: You can now run `./web-lgsm.py --passwd` to change the web admin
    user password for the web-lgsm. Simply run the script then enter the
    required prompts to update the web login password.

2. Question: How do I enable the game server cfg file editor?
  - Answer: The cfg file editor editor can be enabled by setting `cfg_editor`
    to `yes` in the main.conf file.
    - Note: The cfg editor is disabled by default for security reasons, for
      more information see, `docs/config_options.md`.

3. Question: How do I enable the game server console commands Send button?
  - Answer: You can enable game server console commands by setting `send_cmd` to
    `yes` in the main.conf file. This will cause a _Send_ button to appear on
    the controls page. Once pressed, you can then enter the command to send to
    the running game server console.
    - Note 1: Similar to the cfg editor, the game server console commands are
      disabled by default out of an abunance of security precausion. For more
      information see, `docs/config_options.md`.
    - Note 2: This is NOT the same thing as sending shell commands to server.
      If you want to do that use SSH. This option is only for sending game
      server specific console commands to the running tmux session for your
      game server.

4. Question: Why am I getting permission denied when trying to start my newly
   added game server?
  - Answer: Game servers owned by other users require that you add a special
    sudoers rule in order to make the web-lgsm work properly. For more
    information please see, `docs/sudoers_info.md`.

5. Question: I just updated to version 1.6.0 (or greater) from v1.5.0 (or below)
   and now my web-lgsm instance wont start. How do I fix this?
  - Answer: The database changed slightly with the release of v1.6.0. If you've
    just updated to v1.6.0 (or greater) from v1.5.0 (or below) you can run the
    `update-db.sh` script to update your database to be compatible with v1.6.0.
    You may also need to run the `change_pass.py` script as the hash format for
    the password in the database changed slightly. You can change it to the
    same password as what it already was, the hash just needs regenerated.

6. Questions: Where's the `init.sh` script?
  - Answer: In version 1.7.0 the `init.sh` script was replaced with the all in
    one `web-lgsm.py` script. It now does all of the old things the init script
    did plus lots more! Run `./web-lgsm.py --help` to see all options!

7. Question: Why don't any of my sudo rules work? / Why does the web app say
   _"sudo: a password is required"_?
   - It may be the case that you have `/etc/sudoers.d` disabled or have
     additional entries for your user after the `#includedir /etc/sudoers.d`
     line. If so simply move those directives above the `#includedir` line.
   - As man sudoers states:
>   When multiple entries match for a user, they are applied in order.
>   Where there are multiple matches, the last match is used (which is not
>   necessarily the most specific match).


