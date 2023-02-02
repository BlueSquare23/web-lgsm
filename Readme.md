# Web LGSM

## Main Idea

This project is intended to be an easy to use web interface for the [Linux Game
Server Manager (LGSM)](https://linuxgsm.com/servers/vhserver/) command line
tool. The LGSM is a fantastic tool for installing and administering game
servers. However, some users would rather manage their Game server through a
web interface instead. That is what this project attempts to provide.

## Installation

First connect to your game server over ssh and then change directories to
wherever you already have the LGSM installed. In the example below we'll be
using the Web-LGSM with a `Valheim` server.

```
cd /home/$USER/Valheim/
```

Then clone this repository.

```
git clone https://github.com/BlueSquare23/web-lgsm.git
```

Next cd into the `web-lgsm` directory and run the install script. 

```
cd web-lgsm
./install.sh
```

From there you're ready to start the web server.

```
./init.sh
```

Lastly, visit the web servers URL in a browser and enter your game servers name
to start interating with the LGSM via the web. For valheim we'll use the server
name `vhserver`.

## Password Protection & Proxying

If you want to run this web interface on the public internet I would
__STRONGLY__ advise firewalling off the default web-lgsm port 8080 then reverse
proxying connections to the app through a REAL web server (such as Nginx or
Apache) and configuring password protection and SSL encryption!

[Setup Password Auth on NGiNX](https://www.digitalocean.com/community/tutorials/how-to-set-up-password-authentication-with-nginx-on-ubuntu-20-04)

[Setup NGiNX Reverse Proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)

[Setup Let's Encrypt SSL on NGiNX](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)

## Starting & Stopping the Web-LGSM

The web interface can be started and stopped using the `init.sh` script.

* Start Web-LGSM Web Server in the Forground

```
./init.sh
```

* Start Web-LGSM Web Server in the Background

```
./init.sh bg
```

* Stop Web-LGSM Web Server

```
./init.sh kill
```

## License MIT

[MIT License](license.txt)
