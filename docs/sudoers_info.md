# Sudoers Info

In order for the Web-LGSM's automatic game server install feature to work
properly, the install.sh script will setup the following sudoers rule.

```
(root) NOPASSWD: /opt/web-lgsm/bin/python /usr/local/bin/ansible_connector.py *
```

The actual sudoers file will live in /etc/sudoers.d and look something like this:

```
sudo cat /etc/sudoers.d/$USER-$USER
blue ALL=(root) NOPASSWD: /opt/web-lgsm/bin/python /usr/local/bin/ansible_connector.py *
```

This rule allows the Web-LGSM to run its `ansible_connector.py` script, which
wraps the game server installation and delete playbooks, as root without
needing to prompt for a sudo password every time.

The `install.sh` script create the `/opt/web-lgsm` venv and copies the
`ansible_connector.py` scripts and playbook files into system level directories
for security reasons.

Note: If this sudoers rule is disabled the app will no longer be able to
install new game servers or delete users and files for existing installs owned
by other users. Although all other functionality should continue to work as
normal. If you choose to disable this rule as an additional security measure,
feel free! Just be aware it will break your ability to: A) Install new game
servers from scratch, and B) fully delete game servers owned by other system
users, through the web interface.

