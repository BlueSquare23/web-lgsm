# Sudoers Info

In order to allow the web-lgsm to control game servers owned by other users,
you have to manually add a line like the following to your sudoers rules.

```
user1 ALL=(user2) NOPASSWD: /home/user2/gameserver_script
```

Where `user1` is the user the web-lgsm itself is running as, `user2` is the
user the other game server is running as, and `/home/user2/gameserver_script`
is the path to the game server lgsm script file (For example, `mcserver` for
Minecraft, `bf1942server` for Battlefield 1942 ect.).

Use this command to edit your sudoers file:

```
sudo visudo
```

Then add the above NOPASSWD line, filled in with your user setting, to the
bottom of it.

Then your web-lgsm process should be able to manage game servers owned by other
users!

