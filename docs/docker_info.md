# Web-LGSM Docker Information

## Overview

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

1. First run the install.sh script with the --docker option:
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
docker-compose up --build
```

That should build and launch the container.

## Option 2) Running Game Servers in Their Own Containers

The base LGSM project now supports containerizing game servers!

[Official LGSM Announcement](https://linuxgsm.com/2023/07/linuxgsm-introduces-docker-containers-finally/)

Likewise, now so does the Web-LGSM project!

If you'd like to run your game server(s) in a container you can start by
fetching the official `docker-compose.yml` file for your game server.

[Full List on Github Here](https://github.com/GameServerManagers/docker-gameserver/tree/main/docker-compose)

You'll want to replace `/path/to/linuxgsm/` with the path to your
`web-lgsm/GameServers` directory.

For example:

```
# Change this:
    volumes:
      - /path/to/linuxgsm/mcserver:/data

# To this:
    volumes:
      - /home/blue/web-lgsm/GameServers/mcserver:/data
```

Then you should be able to run the following to start your game server in a
container.

```
docker-compose up
```

Once you've started the game server's container, your should be able to add it
to the web interface by going to the "Add an Existing LGSM Installation" page
and selecting install type "docker." From there you should be able to stop,
start, restart, & generally admin your game server in a container through the
web portal as normal.

* **Note 1:** As of v1.8, the config editor for game servers in stand alone
  docker containers doesn't work yet. I never got around to adding this to the
  v1.8 release. But I've got a Todo now to add it to some future release.

* **Note 2:** If you're also running the Web-LGSM app itself inside of a container,
  then you'll need to add other stand along game server containers to the web
  interface as "remote installs." You cant have containers inside of a container.
  So the only way to connect from within one container to another is over SSH
  (aka remote install types).

For more information see [the Official LGSM Github Repo](https://github.com/GameServerManagers/docker-gameserver/tree/main)



