# Web-LGSM Docker Information

## Overview

<span style="color:orange;">_**Note:</span> DOCKER CURRENTLY EXPERIMENTAL!!!**_

There are currently TWO ways in which the Web-LGSM project supports docker.

1. The first option is to run the Web-LGSM Flask app itself within a docker
   container.

2. The second option is to run individual game servers within docker
   containers, and the web app itself on the docker host machine.

Option 2 is probably the best/simplest configuration for most, if your just
want to containerization and isolation for your game servers, but don't so much
care about it for the Web-LGSM application itself.

## Option 1) Running The Web-LGSM in a Docker Container

If you'd like to run the web app itself inside of a docker container you can do
so by following the instructions below.

1. First, if you don't already have docker installed, run the install.sh script
with the --docker option to install docker for Ubuntu:
```
./install.sh --docker
```

2. Next run the docker-setup.py script to built the required docker files. Use
the `--add` flag to add the GameServers mounts and port mappings for any game
servers you'd like to install or add.
```
./docker-setup.py --add
```

3. Finally, run docker-compose up --build to build and launch the container.
```
sudo docker-compose up --build
```

That should build and launch the container.

## Option 2) Running Game Servers in Their Own Containers

The base LGSM project now supports containerizing game servers!

[Official LGSM Announcement](https://linuxgsm.com/2023/07/linuxgsm-introduces-docker-containers-finally/)

Likewise, now so does the Web-LGSM project!

1. First, if you don't already have docker installed, run the install.sh script
with the --docker option to install docker for Ubuntu:
```
./install.sh --docker
```

2. Next find and copy the official `docker-compose.yml` file for your game
server from the LGSM's official list:

[Full List on Github Here](https://github.com/GameServerManagers/docker-gameserver/tree/main/docker-compose)

3. After that you'll want to replace `/path/to/linuxgsm/` with the path to your
`web-lgsm/GameServers` directory in your new `docker-compose.yml` file.

For example:

```
# Change this:
    volumes:
      - /path/to/linuxgsm/mcserver:/data

# To this:
    volumes:
      - /home/blue/web-lgsm/GameServers/mcserver:/data
```

4. Then you should be able to run the following to start your game server in a
container.

```
docker-compose up
```

5. Use `visudo` to add a sudoers NOPASS rule to allow the web-lgsm to run
specific docker commands through sudo without needing a password.

```
sudo visudo /etc/sudoers.d/$USER-docker
```

Add a rule like this:
```
<user> ALL=(root) NOPASSWD: /usr/bin/docker exec --user <server_username> <script_name> *
```

Be sure to replace `<user>` with your system username and `<script_name>` with
the game server's lgsm script name, and `<server_username>` being the user the
game server is installed under within the container.

Here's an example sudoers rule for a Minecraft docker container:

```
sudo cat /etc/sudoers.d/blue-docker
blue ALL=(root) NOPASSWD: /usr/bin/docker exec --user linuxgsm mcserver *
```

6. Finally, you should be able to add your containerized game server to the web
interface!

Go to the "Add an Existing LGSM Installation" page and selecting install type
"docker." From there you should be able to stop, start, restart, & generally
admin your game server in a container through the web portal as normal.

* **Note 1:** As of v1.8, the config editor for game servers in stand alone
  docker containers doesn't work yet. I never got around to adding this to the
  v1.8 release. But I've got a Todo now to add it to some future release.

* **Note 2:** If you're also running the Web-LGSM app itself inside of a container,
  then you'll need to add other stand along game server containers to the web
  interface as "remote installs." You cant have containers inside of a container.
  So the only way to connect from within one container to another is over SSH
  (aka remote install types).

For more information see [the Official LGSM Github Repo](https://github.com/GameServerManagers/docker-gameserver/tree/main)



