## Version 1.1x.x Todos

### PR / Tutorials

* [ ] **Make a github wiki and turn docs into wiki pages**
  - [More info on gh wiki](https://docs.github.com/en/communities/documenting-your-project-with-wikis/adding-or-editing-wiki-pages)

* [ ] **Create new walkthrough video.**
  - [ ] Add links to new Basic Setup & Docker YouTube Videos.

* [ ] **YouTube Video Tutorials**
  - [ ] Mention Patreon or whatever & buy me a coffee link videos.
  - [ ] Mention Discord link in videos.
  - [ ] Basic Web-LGSM Installation, Setup, Key Features Overview (aka Project Update).
    - This is basically a replacement of the existing YT video I have linked in
      the Readme.
    - That video is for v1.3 I think, so pretty outta date now. Kinda still
      works but not using an init script anymore etc.
    - Plus also want to give people an update on the state of the project!
    - Basic Script:
      1. Install the web-lgsm itself, just a normal installation.
      2. Install a new game server via the install page.
        - Show off settings page option for install as new user vs same user.
      3. Add a new web interface user.
        - Explain difference between web inteface user and system level user.
        - Configure some permissions for this user.
      4. Logout then back in as new user and show off newly installed game
         server.
      5. Add a game server via ssh.
        - Will already have one setup beforehand, just need to add it to the web interface.
      6. Add a game server via docker.
        - Will already have one setup beforehand, just need to add it to the web interface.
  - [ ] Full Web-LGSM Docker Installation, Setup, Overview w/ Portainer & Nginx Proxy Manager.
    - The idea here is everything's in a container. 
    - Basic Script:
      1. Install Web-LGSM itself inside of a container.
        - Show off ./install.sh --docker to install docker and other deps.
        - Start the app in a container.
      2. Show how to install one game server inside of the web-lgsm container
         via normal install route. Probably Minecraft. Explain how it works n'@.
      3. Show how to install a different game server inside of its OWN container.
        - The manual way from the cli, fetching docker-compose.yml files from
          their github repo, docker-compose up. 
      4. Show how to add our newly setup sister container to web interface via
         SSH option.
        - Explain how can't install a container when already in a container.
      5. Show both game servers working in app and all that jazz.
      6. Setup Nginx Proxy Manager
        - Add Web-LGSM to proxy manager.
        - Get an SSL cert for it.
      7. Setup Portainer and add containers to it.
        - Add Web-LGSM container to it.
        - Add Standalone Game Server to it.
        - Add Nginx Proxy Manager to it.


## Main Goals for v1.10 -> v1.11

* [ ] **Get this up on docker hub and let people install by just pulling container image**
  - Then add to the readme pull from docker as alt way to install.

* **THE BIG SIX!**
  - [x] File Manager
  - [ ] RPCify The Planet
  - [ ] Interactive Terminal
  - [x] Frontend Overhaul
  - [ ] Docker Beside Docker (w/ docker-proxy setup)
  - [ ] Promotion & Community

* [ ] **Replace shell calls with RPC procedures**
  - No need to job out to the shell now that we have the rpc daemons running.
  - [ ] **Make RPC System handle streaming.**
    - Can't used fix length payload for live console updates.
    - Have to stream off the socket instead. Need to learn how to do that.
      - I'm thinking 90% of procedures will have fixed content length.
      - And header will specify if its fix len buffered or unbuffered...
  - [ ] **Make RPC System work for ssh & docker**
    - SSH is going to be easier but again need to do above todo research first.

* [ ] **Enable remote install over ssh via ansible connector**
  - From the very beginning when I first wrote the ansible connector I imagined
    doing it not only locally but also to remote machines.
  - So you can have your web interface setup on serverA and then install your
    game on serverB.
    - Right now you can manage them over ssh, but never got around to making
      install over ssh work.

* [ ] **Install inside container**
  - The base LGSM project already provides docker compose files for game servers.
  - Need to make an automated 

* [ ] **Docker beside docker**
  - Thought is:
    - Main app in container
    - Install into container
    - Use docker-proxy to talk between containers securely

### Misc Immediate Todos

* [ ] **Finally do away with old `utils.py` (aka `utils/helpers.py`) file**
  - Global includes in here are breaking a bunch of stuff.
  - Should've never `include *` from there. Oh well live and learn.

* [ ] **Explore old INLINE TODO's for v1.9.0 and see what's most important**
  - For the biggest stuff either fix there on the spot (if able) or make a todo
    below for later.
  - But want to try to clean up some of that backlog.
  - Just run `grep -R TODO app/*` to find em all!

* [ ] **Try to make draft version of pie in the sky custom command web-modules**
  - So like users could define custom command modules and add them to the page
    as specialized buttons or whatever to do the needful.

* [ ] **Allow in app game server moves**
  - This should be integrated with the in app file browser whenever I get to that. 

* [ ] **Pythonify and Deshellify as much as possible**
  - Too much of this app is misc bash code doing more than it should with
    questionable validation / sanitization.
  - I've always written it off as "Its all behind auth anyway" which is true,
    but that's really not a great excuse. 
  - I need to transition like everything besides the core web-lgsm scripts
    themselves to be pure python and lock down all non-intentional leakage best
    I can.
  - This is going to take some core redesigns which I haven't had time to
    experiment & come up with yet.

* [ ] **Restructure application and build out proper API**
  - [ ] Setup proper external API Keys for api auth only that can be used with
    this app besides having to establish a session token first.
  - Ideally, the pages should just be an interface that communicate via rest-ish
    JSON to apps API endpoints.
  - Right now views routes / functions are handling waaayy tooo much logic. Whole
    apps functionality happens via views functions. All this should be
    happening via the app's API routes and just strung together by views logic.
  - [ ] I've been doing so much by hand but it might be worth taking some time
    to experiment with FastAPI to help me truly build out this API and swagger
    docs.
    - https://fastapi.tiangolo.com/
  
* [ ] **Get app up on docker hub**
  - Should distribute via dockerhub too. Right now have experimental docker
    compose, that needs some love too.
  - But we'll get way more users if we just publish on docker and let people
    run it in a container they can teardown whenever.

## Version 1.1x.x Todos

* [ ] **Rewrite xtermjs code to fix live console output & to fix carriage returns prints.**

* [ ] **Add more Custom Themeing options to config**
  - So I've already got a couple of color options for the config.

* [ ] **Rename ansible_connector.py**
  - This is doing more than just running playbooks now. In truth it always has been.
  - Really its more like the root system connector, with running ansible
    playbooks as a side gig for it.
  - I think at the very least the name needs changed. Still workshopping new name ideas.
  - But might also be a hint that larger components of the app need to change too...

* [ ] **Think more about adding auth to rpc servers**
  - Right now not too worried about it since the socket file perms do the heavy
    lifting here. Also no one is hacking my shitty little web app.
  - But probably not a terrible idea to add it later on down the road.
  - But also torn because its all on the same system. Seems silly for the main
    app user/pid to have to use secrets to talk to its children. Like some
    hacker with a shell on the system as the web-lgsm user could just dump those
    secrets and then talk to all the child servers.
  - Have to do some more thinking.

* [ ] **Future File Manager Features**
  - [ ] Create Directory
  - [ ] Move file / directory
  - Non-day1 stuff.
  - [ ] It'd be cool if could return info about mime type with file contents.
    Then we could set the CodeMirror extension to be the same so syntax
    hightlight always works. We might even just be able to use the file extention
    tbh.
  - [ ] Full support for file manager over SSH and in docker via module scripts.
    - These module scripts are handy, might as well use them over ssh and
      inside of a container if we can.
    - So they need shipped and installed there somehow...

* [ ] **More tests**
  - [ ] Unit Tests for FileManager
  - [ ] Integration Tests for edit file as alt user after install

* [ ] **Make Multi-User RPC Service work over SSH and inside of Containers**
  - They work great as same and alt user.
  - Its very nice to have an interface that wraps up and runs the same code run
    in two different ways.
  - All the pieces are already there:
    - We have an ssh remote runner.
    - We run docker cmds via cli runner.
  - Instead of running shell over docker tunnel or ssh we run shell to module
    script's `cli.py` and bobs your uncle.
  - Wanna do it smartly tho, keep things from becoming too coupled...
  - But its all infra layer stuff and with this out of the way we no longer
    have to worry about maintaining both shell for docker and ssh server and
    pure python for local. It can all be PURE PYTHON! Better for security and
    maintainability.

* [ ] **Add sliding session expiration (aka session renewed every request) to user login**
  - Basically, we want so that if the user visits the web app often enough,
    just keep them logged in indefinitely. But we don't want to have really
    long session tokens because, csrf, click jacking, other problems.
  - I gotta read more about this, figure out how it fits in with Flask-Login
    and if it conflicts with their "Remember Me" mechanism.
  - https://flask-login.readthedocs.io/en/latest/
  - Also I wonder if I can just cheese it and say "if authed already, just
    update remember me cookie expiration." That might require a full
    `login_user` call, idk yet. But think that might be fine...

* [ ] **Add install new game servers to containers**
  - Instead of installing as new system users, allow install game servers
    inside of containers.
  - Might even be able to use the pre-made containers from LGSM.
  - And/Or tell users manually create the ports.
  - And/Or just let them directly access and edit the yaml via web file editor.

### New Features

* [ ] **Add collapsible sitemap accordion panel to righthand side**
  - Goal is get to any page from any page by opening up side panel and going
    into that section.
  - Hypothetical Sitemap Layout Tree:
```
Home
    GameServers
        Edit GameServer Cfg File
        Add or Edit GameServer Install Details
        Edit GameServer Jobs
        Install New GameServer
        GameServer Controls
    App
        Settings
    Admin
        Edit Users
        Audit
    Auth
        Setup 2FA
        Logout
    Misc
        About
        Changelog
        Swagger Docs
```
  - That kinda doesn't work exactly cause like for game server pages you need
    to specify what gameserver you're working with. But its roughly how things
    are.
  - Notes for Nick:
```
So we're using Bootstrap 5.3:
https://getbootstrap.com/docs/5.3/getting-started/introduction/

I think you should be able to use this Accordion stuff they have.
https://getbootstrap.com/docs/5.3/components/accordion/

And then wrap that accordion in a collapsible side thing. And maybe that open / close button into the existing navbar.
https://getbootstrap.com/docs/5.3/components/collapse/#horizontal

If you need any icons, we're also using bootstrap icons, so you can just use any of these css classes like this <i class="bi bi-0-circle"></i>
https://icons.getbootstrap.com/
```

* [ ] **Add Login IP address to Audit Log for Logins**
  - Should say: `User 'username' logged in from 1.1.1.1`

* [ ] **Address CodeQL Alerts**
  - https://github.com/BlueSquare23/web-lgsm/runs/62909674268
  - Yeah I know accepting keys blindly is bad, but need to do more research to
    see what we can really do about it.

* [ ] **Make web-lgsm.py update json work again for new game servers**
  - I broke this when I added pictures. 
  - [ ] Tbh whole json file needs restructured like this instead:
```json
[
   "Assetto Corsa": {
    "script": "acserver",
    "name": "Assetto Corsa",
    "img": "https://cdn.cloudflare.steamstatic.com/steam/apps/244210/header.jpg",
   },
   ...
]
```

* [ ] **I need a public site for the project**
  - Not only do I need to catch form posts for usage stats and crash reports,
    but it'd be nice to have somewhere with all the links to be like yeah this
    is legit.
  - Basically can just be same as readme and about page.
  - I'm thinking I just make a branch of the main flask app an spend a few
    bucks on a .com.
  - We can throw it up on my VPS at work its fine.

* [ ] **Add option for anonymous usage statistics.** (This might have to wait :sigh:)
  - This is not technically difficult, as in setting this up from a software
    perspective would be relatively simple.
  - Thing is I don't know about the regulatory side and how that applies to me
    as a single creator of a simple web app...
  - Pretty sure all of these regulations mean I need to get user consent first:
    - GDPR (General Data Protection Regulation)
    - CCPA (California Consumer Privacy Act)
    - COPPA (Children's Online Privacy Protection Act)
  - So thinking maybe after initial install & login form pops up that says "do
    you want to send anonymous usage stats?"

* [ ] **Crash reports**
  - This kinda goes along with the usage stats. Might not really be easy. Idk I
    might have to look at gunicorn and see if there's something we can do to
    catch 500's and send a stack trace and maybe some anonomized vars dump back
    to me somehow. (Email sucks so prolly just post to a site I control)

* [ ] **Get fully working shell interface through web terminal**
  - This would be a direct passthrough to a live shell session running as the
    user with stdin, stdout, stderr of the node xterm session plugged directly
    into 0,1,2 of an underlying shell session running as the user for that game
    server.
  - Like many of other *spicy* features, this will ship DISABLED by default.
  - Mainly I just kinda want to see if I can do it. 
  - Would be dope if it could work as any user that web-lgsm has access to.

### The Rest

* [ ] **Find way to detect available server controls on a per server basis**
  - I'm thinking the existing `json/controls.json` file isn't going to cut it anymore.
  - I'm pretty sure there are plenty of servers that don't have the exact same
    normal options and ones that have special options. 
  - So I'm thinking at first controls page load for new server we detect options
    and store them to DB for GameServer.

* [ ] **Break up form classes into one class per file**
  - Just makes things easier to find.
  - I don't care if some will be tiny, that's a hint more validation might be needed...

* [ ] **Add two new main.conf proxy related things**
  - 1. Add `trusted_domains` list to [server] section for reverse proxied
    setups so swagger docs display correct name.
  - 2. Copy this guys changes for situation where app needs to use http proxy
    to talk to outside world.
    - https://github.com/BlueSquare23/web-lgsm/compare/master...rqdmap:web-lgsm:master
    - Since these are just env vars, think I can just put them in the app init
      and then pass the env in. Not sure why he put them in the old
      run_cmd_popen, perhaps because they were not needed elsewhere.

* [ ] **Write unit tests for new untested classes**
  - Classes still somewhat molten, once more arch decisions made and classes
    harden, then more through testing makes sense. Right now this code is
    working but some what temporary.

* [ ] **Change docstrings to use Sphinx and look into auto generated readthedocs with it**
  - I've been using a made up fake docstring format. Time to change that to be Sphinx.
  - https://docs.python-guide.org/writing/documentation/#sphinx
  - https://www.sphinx-doc.org/en/master/
  - This might be the sort of thing I can get help with from an llm, but we'll see.

* [ ] **Cleanup render template calls with kwargs packing**
  - I can just shove all the stuff in a kwargs dict before calling render
    template. Would make things look nicer, easier to read.

* [ ] **Continue fixing up tests**
  2. [ ] For Assert step, CHECK MORE STUFF VIA THE DB DIRECTLY!!!
    - I really need to be taking an action, then checking the DB.
    - I'm checking a lot of responses from the outside to make sure they're as
      expected. However I'm not really checking directly in the DB itself to
      make sure things are all good.
    - But I can do that, so I should be doing that. Oh well always more things
      to do than time to do them.

* [ ] **More Cron Improvements**
  - [ ] Add `@reboot`, `@daily`, `@hourly`, etc. to cron scheduler.
  - [ ] Add option to send stderr or stderr & stdout to file (default /dev/null)
  - [ ] Add "adopt" for unmanaged jobs to add them to DB and associate with game server.

* [ ] **Add Sudo Pass Form for cmds that need it**
  - Things like app update (and maybe even install again) need a sudo password
    to run.
  - Not sure how to hack this into existing sudo invoked stuff atm cause its
    gonna wanna read stdin. Problem for tomorrow me!

* [ ] **Fix the in app update!**
  - This requires sudo password form.
  - I think this is still broken which sucks.
  - You should be able to update the app from the web panel.

* [ ] **Add new export database information**
  - I want to allow users to export their database to csv or json or something
    for backup / manual update / migration purposes.

* [ ] **Create service layer class for controls page & add api route**
  - [ ] Basically build out api routes for buttons on controls page.
    - `/api/controls/<server_id>`
  - [ ] Also build out new class for controls service layer.
  - [ ] Make both API and Route code use this new neutral service class to
    actually do the needful.

* [ ] **Make config options display on page if debug true**
  - Makes sense and I've seen other web apps do this sorta thing before. Just
    pipe that info right to page if debug is true.
    - Not a big priority for v1.8 release.

* [ ] **Make install_path an optional main.conf parameter.**
  - By default I want to set this to just `/home/<user>/<server_name>`.
  - But then allow people to put it where ever for their own purposes.
  - Write tests for this.

* [ ] **Make cfg editor work for `install_type` docker.**
  - Never got around to making this work for the v1.8 release. Just had too
    much stuff to get done so this got left out.
  - Basically, I just need to make `find_cfg_paths()` work for
    `server.install_type` 'docker' too. Already works for remote and local.

* [ ] **Write `ssh_connector.sh` shell script.**
  - Basically if I want to limit access to multiple commands over ssh I need to
    do something like this: https://serverfault.com/questions/749474/ssh-authorized-keys-command-option-multiple-commands
  - I think doing this in bash is probably safe enough.
    - Will just have to validate cmds are legit.
    - Will cross `send` command bridge when we come to it. 

* [ ] **Allow remote game server installs over SSH.**
  - I already have a lot of the install process setup as playbooks anyways.
  - Would just need to do install type remote `./gsserver ai` via
    `run_cmd_ssh()` instead of using ansible connector.

* [ ] **Re-write routes to be all api based.**
  - I know it might seem tedious, but what this will give me is an api that
    other people could use to do whatever they want.
  - I'd be not only creating a web management interface for the lgsm, but a
    whole web api.
    - The app currently can be used like this already. A user could make GET
      requests to the controls endpoints easily to start / stop / restart etc.
    - However nothings in real REST format, can't do it in json, its all GET
      requests when it should be POST's if it were an api, etc.

* [ ] **Build out support for Fedora, Rocky Linux, & AlmaLinux.**
  - These are all of the linuxes supported by the base lgsm project.
    - https://docs.linuxgsm.com/linux/distro
  - I don't anticipate this being too difficult...
  - The install script needs updated.
  - The tests need re-ran on all the linuxes.
    - [ ] Maybeeeee I could setup custom gh action runners for these os's.
      - https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners
    - But that seems like a lot, so might just only have CI for the Ubuntu one,
      and I'll have to remember to just manually run the tests against and play
      with the others before release.

## Backlog

* [ ] **Setup github pages to host Swagger docs for project w/ github actions**
  - https://github.com/peter-evans/swagger-github-pages

* [ ] **Add Python Selenium end-to-end tests to actually login and do a bunch of
  stuff in the web interface.**
  - Try to thoroughly test site functionality, basically redo all of the same
    things the functional tests do through raw GET/POST requests, but instead
    through the selenium browser.

* [ ] **Add export game servers list to json (admin only).**
  - Allow admin users to export a list of currently installed / added lgsm game
    servers to json.

* [ ] **Add import game servers list from json (admin only).**
  - Basically I want to make it easy for people to re-install or migrate
    instances, etc.

## Pie in the Sky

Maybe I'll do these things but really they're all just kinda dreams for now.

* [ ] **Custom Commands on Control Panel**
  - I don't really want to make this just another webshell/rce panel/linux web
    gui. I think there's enough of those already out there in the world and
    obviously would be a huge security hole.
  - Instead, what I want to do is create a user extensible way to allow them to
    create their own custom dashboards for managing game servers.
  - I think the idea here would be users can define custom command objects
    inside of a json conf file.
    - Example:
```json
{
  "uptime": {
    "command": ["/usr/bin/uptime"],
    "description": "Gets system uptime",
    "type": "daemon",
    "refresh": 5
  },
  "temp": {
    "command": ["/usr/bin/sensors"],
    "description": "Gets system cpu temperature",
    "type": "daemon"
    "refresh": 60
  },
  "custom": {
    "command": ["/path/to/custom.sh", "arg1", "arg2"],
    "description": "Custom button",
    "type": "button"
  }
}
```
    - Those will then be parsed and loaded by the app.
    - I think I want to limit these to showing up on the controls page.

* [ ] **Add more thorough tests over SSH.**
  - Setup a remote host with Minecraft on it.
  - Add flag to web-lgsm.py to do `--test_ssh`.
    - Don't run this as part of ci/cd.
    - Can't add a priv key so can't connect the ci tests to a remote host.
    - This would just be for me to run manually every so often to check
      everything over remote ssh is all good.

* [ ] **Look into Conda/Mamba as a better way of packaging project's system dependencies.**
  - I would get more control over specific package builds and would be platform independent.
  - But then I'd have to use that to manage all the packages n'@ and people are
    less familiar with these sorta 3rd party pkg managers.

* [ ] **Add cool retro term style customization options**
  - I played around with some css for adding cool term effects to the xterm.js
    window. Would need a lot of integration to pass user prefs back to the
    javascript code where they're set. So will play around with that more another
    time.

## Disclaimer

This document is basically just a rubber ducky for me while I change things.
Its just a scratch pad to jot things down on and throw ideas in when I maybe
don't have time to work on them right then.

It is the main way I keep track of what needs done for the project so it is a
highly in flux document on the dev branch. Not all of these ideas make sense or
are going to work or make it into the final release.

```
      ,~~.
 ,   (  - )>
 )`~~'   (
(  .__)   )
 `-.____,' 
```

[Ascii Art by Hayley Jane Wakenshaw](https://www.asciiart.eu/animals/birds-water)

