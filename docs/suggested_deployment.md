# Suggested Deployment

By default this web application runs on localhost (127.0.0.1) port 12357. If
you're going to run the web-lgsm on the public internet its advisable to
firewall off the default port for this app and reverse proxy connections to it
through a **real** web server such as Apache or Nginx with SSL encryption!

There are a million ways to deploy either of those solutions so I'll leave that
part up to you. However, if you need a place to get started I'd advise using
the [Nginx Proxy Manager](https://nginxproxymanager.com/) docker container.
This will allow you to setup both reverse proxying and get a Free automatically
renewing SSL certificate for your domain.

