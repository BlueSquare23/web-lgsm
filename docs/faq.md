# Frequently Asked Questions

1. Question: I forgot my web-lgsm password, how do I reset it?
  - Answer: Unfortunately, as of right now (v1.6) there is no official password
    reset mechanism. While it is technically possible to update the password
    hash stored in the database with a sqlite cli command, for most users I
    reccomend just deleting the `app/database.db` file and restarting the app
    to set up the login fresh again. This has the downside of removing any
    entries stored in the web-lgsm already. But once logged back in you can
    simply re-add them using the "Add an Existing LGSM Installation" page.

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

5. Question: I just updated to version 1.6 (or greater) from v1.5 (or below)
   and now my web-lgsm instance wont start. How do I fix this?
  - Answer: The database changed slightly with the release of v1.6. If you've
    just updated to v1.6 (or greater) you can run the `scripts/update-db.sh`
    script to update your database to be compatible with v1.6 and beyond.
