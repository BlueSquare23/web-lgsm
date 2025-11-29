## Version 1.8.0 Todos

### v1.8.0 Pt 6. Post Release PR / Tutorials

* [ ] **Add new docs & Fix existing docs.**
  - A decent amount of review needs done here, I haven't even begun to look but
    probs going to be a lot.

* [ ] **Make a github wiki and turn docs into wiki pages**
  - [More info on gh wiki](https://docs.github.com/en/communities/documenting-your-project-with-wikis/adding-or-editing-wiki-pages)

* [ ] **Create a discord server for project / community**
  - [ ] Update community docs to also point to discord server.

* [ ] **Fix up Readme.**
  - [ ] Update Readme gifs with newest look of interface.
  - [ ] Add links to discord server.
  - [ ] Add links to new Basic Setup & Docker YouTube Videos.
  - [ ] Add contribute section pointing users to submitting an issue or submitting a
    pull request.
    - I have the community docs for this now.

* [ ] **Setup a Community Discord Server**
  - Some people might have simple sorta support questions or ideas in there.
    I'll try to remember to check it every once in a while.
  - [ ] Add link to discord to Readme!

* [ ] **Create Patreon or Ko-fi donation platform**
  - Actually had a user request this. Doesn't seem too hard to setup and even
    if only a few people give, still could be nice to get a few extra bucks a
    month.
  - [ ] Add link to Readme.

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
  - [ ] Add "OLD VERSION" to the title of old video.
    - [ ] Also link to newest video in the endcard and description.
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


## Main Goals for v1.8 -> v1.9

* [ ] **Improve overall design & documentation for project**
  - I want to actually properly try to design, document, and build out parts of
    this app. Full honest, I've never really done real software design before
    and this app up until this point (2025) was build with nothing but loose design 
    ideas and hopes and dreams.
  - This lack of design has fucked me and hampered the future development of
    this app. Oh well live and learn.
  - Major goal moving forward is to properly think, read, test, mockup, design,
    document, then build.

* [ ] **Straighten out plans for new models for data and actions / Begin OOP Redesigns**
  - This project has been poorly designed and modeled up until this point.
  - I am now beginning the process of redesigning the project piecemeal while
    maintaining functionality.
  - What I really need to do is:
    - Figure out what Objects I need
    - Figure out what they need to do
    - Figure out how they need to relate to each other
    - Figure out how to get from here to there, bit by bit
  - https://realpython.com/solid-principles-python/

* [ ] **Validation logic should happen in the form classes**
  - FlaskForm/Wtforms is our user input handling & validation layer.
  - All user input coming into the app, even through the API should go through
    a form class for valiation.

* [ ] **Create new neutral backend service layer interface class(es) to house business logic and be used by both route and api code**
  - The idea here is twofold:
    1. I want the app to have a mature api, where basically anything you can do
       through the web, you can also do through a curl cmd.
    2. I also want the app's route logic to still use things like Flask-WTF/WTForms validation.
  - To accomplish this, I'm going to slowly transition existing routes to use
    new service layer classes. New features will just be built this way from
    the start. Old features will be transitioned over time.
  - See new cron.py for example of `CronService` class to act as intermediary
    between API and DB (model). 

* [ ] **Reduce redundancies in disparate isomorphic representations of the same data**
  - I have too many different representations of the same underlying data.
    - There's the data in the DB.
    - There's the data on disk, in flat json files.
    - There's the data on disk about game server state.
    - There's the data returned from game server commands.
    - There's the validation of the data in the form classes.
    - There's the validation of the data in the utils.
    - There's data in the `processes_global.py` singleton in memory.
    - Its all over the place.
  - I think the idea of creating neutral service classes that can be used by
    the API or by the Route code to talk to the DB is a good start.
    - But part of me also wonders if its just more bloat.
  - Basically, I can see the same shapes and imprints of those shapes all over.
    But I have yet to come up with a good way to like bring all that together
    under like the same class or something.
  - I'm optimistic that as I redesign and make more things OOP, some of the old
    poppycock-nonsense will naturally unfold.

* [ ] **Enable remote install over ssh via ansible connector**
  - From the very beginning when I first wrote the ansible connector I imagined
    doing it not only locally but also to remote machines.
  - So you can have your web interface setup on serverA and then install your
    game on serverB.
    - Right now you can manage them over ssh, but never got around to making
      install over ssh work.

* [ ] **Rethink main design to sandbox things even more**
  - Right now the web -> db -> ansible connector as root way of administering
    the system has me nervous.
  - There's validation, there's sanitization. But the whole approach seems bad.
    - Too much happening as root!
  - I've waffled with this so much and decided on the connector script as a
    necessaity to package up all the escalted dirty work in one script.
  - But its overloaded and its data channels are too wide and I suspect leaky.
    - A new approach is needed.
  - Running as the new user through sudo maybe the preferable way over
    backwardsass ssh to localhost approach.

* [ ] **Get fully working shell interface through web terminal**
  - This would be a direct passthrough to a live shell session running as the
    user with stdin, stdout, stderr of the node xterm session plugged directly
    into 0,1,2 of an underlying shell session running as the user for that game
    server.
  - Like many of other *spicy* features, this will ship DISABLED by default.
  - Mainly I just kinda want to see if I can do it. 
  - Would be dope if it could work as any user that web-lgsm has access to.

* [ ] **Try to make draft version of pie in the sky custom command web-modules**
  - So like users could define custom command modules and add them to the page
    as specialized buttons or whatever to do the needful.

* [ ] **Build (or otherwise integrate with existing) web based remote file browser / mod manager**
  - Seems like the community wants an FTP-like web interface.
  - Building this myself from scratch would take a ton of effort and time that
    I don't really have tbh. Unless people are willing to be very patient.
  - A better road would be to integrate someone else's existing web based file
    browser into my project. There is one Flask extention for file browser I
    saw but it sucks and I don't want to use it and I can't use it for over ssh :(
  - So still no idea how to do this but might end up having to write it mostly
    from scratch.

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
  
* [ ] **Use Web Sockets for realtime communication**
  - The console for this thing is just some inefficient jquery contently making
    requests back to api endpoints. It works, but its a hacky mess. 
  - I want to transition the app to use web sockets for this communication
    instead.

* [x] **Overhaul & Redesign test code**
  - [x] Every single test should be idempotent (they're not rn).
  - [x] No test should depend on any other test (they all depend on each other rn).
  - [x] I need to learn more about how to actually fucking properly use pytest (rtfm).
  - [ ] Bonus points: If I can get some Selenium tests in here.

## Version 1.8.7 Todos

* [x] **Move config management stuff into its own class**
  - I'm making an effort to clean up the `utils.py` file.
  - First thing to do is take those ugly functions in the utils file and move
    them into their own class and update the app code and tests.
  - [x] Then write some unit tests for the new class n'@.

* [x] **Refactor main app `__init__.py`, offload flask extensions code to own file(s)**
  - I'm using flask extensions for logging and DB stuff, etc.
  - This code is clogging up the main `__init__.py` and that things a mess.
  - I know there's better ways to organize flask extension stuff, I've just
    never really looked into it.
  - Time to do that!

* [x] **Break up apps blueprints into dir**
```
└── blueprints/
     ├── main/
     │     home.py
     │     controls.py
     │     settings.py
     │     ...
     ├── auth/
     │     login.py
     │     logout.py
     │     two_factor.py
     │     ...
     └── api/
           cron.py
           console.py
           ...
```

* [x] **Break up models into separate class files.**
```
└── models/
    ├── __init__.py
    ├── user.py
    └── game_server.py
    etc.
```

* [x] **Convert blocklist.py into blocklist_service.py class and make singleton**
  - Right now just threw that in there quick and dirty as a module level singleton. 
  - But with all the other restructures, needs its own class file made proper singleton n'@.

* [x] **Make real singleton to hold proc_info objects**
  - I've been using a module level singleton, but this sucks.
  - Might as well just put it in a real class.

* [ ] **Write unit tests for new service layer classes before get too behind**
  - Gotta write tests for these:
    * `BlocklistService`
    * `ControlsService`
    * `ProcInfoService`

* [ ] **Make redirect to github on about page open in new tab.**

* [ ] **Add buy me a coffee link to about page author section**
  - My buddies opinion is that it should be prominent on the page.
  - I don't really care to much tbh, but I'll do it for him.

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

* [ ] **Remove custom tmux socket file name caching in favor of flask cache**
  - I wrote the custom caching stuff before I was really using flask cache.
  - Now I need to rip all that code out and replace it with buitin cache code.
  - Not super urgent though cause old code works fine.

* [ ] **More install configuration options!!!**
  - Users should be able to set other things via the install form!
  - They should be able to set:
    - `install_name`
    - `install_path`
    - `username` 
    - `install_host` 

* [ ] **Add reverse_proxy main.conf var to [server] section for setting name through rev proxy**
  - [ ] Then pipe this var through to API where it get's hostname and if
    `rev_proxy` name is set, use that instead.
  
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

* [ ] **For install list do sort by alpha two columns header**
  - At the top of the install page, add some buttons to sort by alphabetical
    order for both columns.
  - Right now order is ascending by server short name.

* [ ] **Change sort order of game servers on main page**
  - User wants the ability to change the ordering of the GameServer items on
    the home page.
  - Either sort alphabetically or custom order.
  - [Related Issue](https://github.com/BlueSquare23/web-lgsm/issues/55)

* [ ] **Continue fixing up tests**
  2. [ ] For Assert step, CHECK MORE STUFF VIA THE DB DIRECTLY!!!
    - I really need to be taking an action, then checking the DB.
    - I'm checking a lot of responses from the outside to make sure they're as
      expected. However I'm not really checking directly in the DB itself to
      make sure things are all good.
    - But I can do that, so I should be doing that. Oh well always more things
      to do than time to do them.


## Version 1.8.x Todos

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

* [ ] **Allow multiple auto installs of same game server as new user, just increment
  the name.**
  - So first mcserver install would just be mcserver but then a second one the
    user would be mcserver2, mcserver3, etc.

* [ ] **Make PATHS options configurable in main.conf**
  - What I'm thinking is that the main.conf could have a section for [paths]
    and then specific utils paths could be set in there and passed through to
    the web app.
    - For example:
    ```
    [paths]
    cat = /bin/cat
    ```
  - [!] Might kinda be a security issue, have to think more about how to do
    this safely. Maybe only allow paths under the user real PATH var...

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

* [ ] **Introduce more oop concepts to project / slowly transition to more oop.**
  - [ ] Modularize utils functions using SOLID principals.
    - This whole project can be broken apart more. Too many functions don't
      really make sense and are doing too much.
    - Everything should just do one thing.


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

* [ ] **Fully integrated file explorer for managing files and mods**
  - Idea here is to clean up the existing edit page and add in a file manager.
    - So right now file manager takes as input the full path to files. This is
      dumb as hell. It should only take in relative path to game server's base
      dir. Keeps url looking cleaner + implicitly limits to game server dir.
  - I'm not super thrilled with the idea of doing a full file manager by
    wrapping shell commands. But designwise I've sorta backed myself into that
    corner. How else do I do it over ssh, most of the app works over ssh.
  - There are hacky ways to run native python over ssh, but that's really not
    much better than just using shell commands.
  - I think it'll be okay if I just do these operations:
    - list
    - edit
    - delete
    - create
    - upload
  - Just like the file editor it'll be disabled by default and users will have
    to opt-in to enable it. And won't be accessable from setting page.
  - This will take some work to do properly and safely. But we'll figure it out.


* [ ] **Add more thorough tests over SSH.**
  - Setup a remote host with Minecraft on it.
  - Add flag to web-lgsm.py to do `--test_ssh`.
    - Don't run this as part of ci/cd.
    - Can't add a priv key so can't connect the ci tests to a remote host.
    - This would just be for me to run manually every so often to check
      everything over remote ssh is all good.

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

