# Web-LGSM Docker Information

## Running The Web-LGSM in a Docker Container

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

## Running Game Servers in Their Own Containers

TODO
