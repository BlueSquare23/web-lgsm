## Version 1.8.0 Todos

### PR / Tutorials

* [ ] **Get this up on docker hub and let people install by just pulling container image**
  - Then add to the readme pull from docker as alt way to install.

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


## Main Goals for v1.9 -> v1.10

* [ ] **Revamp the interface design and layout**
  - I'm not much of a front end guy. However, this project has simply come too
    far with the original design / layout of the main pages and it needs an
    overhaul.
  - What I really want is a more web 2.0, discordesque design. 
  - For example, one idea I had was a panel that comes out from the side with
    different sections for navigating the app. Rather than the current "Other
    Options" list on the home page.
    - Then you could get to any page from any page and is a more comfortable
      way people are used to navigating web apps.
    - So would need to come up with an accordion of app's sorta hierarchy and
      page structure. Something like this for example:
      - Home Page
        - Same Installed List, but more configurable settings for them
          - Sort by user, Alpha, Custom Order.
        - Stats
        - Links
      - GameServers
        - Controls
        - Jobs
        - Configs
        - Install
        - Edit
      - Settings
        - App Settings
        - User Settings
    - That's just an example, I've also toyed around with the idea of the home
      page having the terminal on it and then install or commands somehow both
      display through that main single and only terminal. Like the apps built
      around the central terminal device.
      - I really like this idea but I have no idea how to impliment it.
  - And yeah just overall learn some more CSS and put some more time into the
    frontend of this app to really make it spiffy and nice.
  - The frontend's kinda always been an after thought. Like oh shit I need an
    interface let me put some buttons on a page real quick and tweak the
    default bootstrap styling.
    - And that works fine, but its nothing to write home about. I want this to
      be spiffy and to shine.

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

* [ ] **Get app up on docker hub**
  - Should distribute via dockerhub too. Right now have experimental docker
    compose, that needs some love too.
  - But we'll get way more users if we just publish on docker and let people
    run it in a container they can teardown whenever.

* [x] **Overhaul & Redesign test code**
  - [x] Every single test should be idempotent (they're not rn).
  - [x] No test should depend on any other test (they all depend on each other rn).
  - [x] I need to learn more about how to actually fucking properly use pytest (rtfm).
  - [ ] Bonus points: If I can get some Selenium tests in here.

## Version 1.9.1 Todos

### New Features, Highlevel Release Goals

* [ ] **Continue re-architecture efforts**
  - Problems:
    - Too many "services" that aren't services.
    - Lacking conceptual models for what they are.
      - As a result haven't decided where to put them yet.
    - Not a clean arch currently, therefore ugly dep inversion happening for manager classes.
      - Need to figure out how do I give both my routes access to services and
        my managers access to services while avoiding circular imports. 
      - I could just use dynamic imports, but I'm convinced there's a better way
        if I could just figure out how to better lay out all the pieces.
    - Managers shouldn't depend on services, but right now they do depend on
      services. So I'm using dep inversion. But that's nasty and I don't like
      any of that. And its kinda just a word soup anyways with servics vs
      managers not really meaning much.
  - Solution:
    - A Clean Arch Transition: I'm going to go feature by feature and convert
      them to be clean arch.
    - Probably going to start small till I get what I'm doing and then will do
      all the bigger stuff too.
    - This will give us a clear dependency graph and a skeleton we can use to
      continue the project's growth.

* [ ] **Do a basic security audit, identify and patch holes, and improve validation**
  - Okay there's plenty of things about this app and codebase that are _suss_.
    Not intonationally, its just if you're going to build something like this
    it involves risks.
  - But at the very least we can go through and find holes and try to patch
    them up.
  - Mostly right now I'm concerned with things slipping past validation, and
    with the amount of shell code that should really be python. If we can cut
    those things down, we gain a lot more security.
  - Also some pip requirements need updated.

* [ ] **Find way to detect available server controls on a per server basis**
  - I'm thinking the existing `json/controls.json` file isn't going to cut it anymore.
  - I'm pretty sure there are plenty of servers that don't have the exact same
    normal options and ones that have special options. 
  - So I'm thinking at first controls page load for new server we detect options
    and store them to DB for GameServer.

* [ ] **Cron Add Listing of All Jobs for Admins**
  - For jobs that are in the crontab, but not in the database (aka ones not
    controlled by the app), show them for admins, but greyed out.
  - User Requested: https://github.com/BlueSquare23/web-lgsm/issues/49

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

* [ ] **Add more control over display of main servers listing on home page. Add sort, custom order, etc**
  - User requested feature: https://github.com/BlueSquare23/web-lgsm/issues/55
  - Yeah shouldn't be too hard just some JS and maybe we store some custom order pref in the db or something too.

* [ ] **Clean up misc messes and add more unit tests for untested classes**

* [ ] **Explore old inline TODO's for v1.9.0 and see what's most important**
  - For the biggest stuff either fix there on the spot (if able) or make a todo
    below for later.
  - But want to try to clean up some of that backlog.
  - Just run `grep -R TODO app/*` to find em all!

* [ ] **Do a Docs Audit/Refresh**
  - Basically there's old dead info in some of the docs files still. I just
    need to go through each one read it and check its info is still up to date.

### The Meat

* [x] **Redo cron as clean arch**
  - [x] We need an abstraction in the core. Aka domain layer `Cron` domain entity class.
  - [x] We need a `CronRepository` in the domain layer too.
  - [x] In the application layer we need to define some Usecases.
  - Aka these need converted to cron use case classes:
    - [x] `list`
    - [x] `delete`
    - [x] `create`
    - [?] `edit` - The app sorta presents this as a different use case, but its
      the same form, same validation, same thing if its creating brand new or
      editing existing, still needs all the same info. So for now not making an
      identical usecase.
  - [x] Probably we can reuse a lot of existing code for the Infrastructure layer,
    but it will need split.
    - [x] We can put the mysql stuff in one class like the SqlAlchemyAuditRepo` stuff
    - [x] Then the system cli cron stuff will need to be split out.
  - [x] Container Wiring needs updated to pull everything together.
  - [x] Route code will need updates to use new calls!
  - Only thing I'm nervous about is all the interaction with still non-clean
    CmdService stuff. But we'll clean that up in time and update the infra
    accordingly.

* [ ] **Figure out how logger fits into clean architecture**
  - It'd be really nice to get more info out of some of these deeper errors to
    help catch bugs and because I don't totally know what I'm doing yet.
  - But it feels wrong to push the normal logger down into those.
  - I mean I rarely even put the logger in utils functions when I still had a
    million of those.
  - I could be wrong, but the logger seems like an interface layer thing.
  - So then how the heck do I get info outta those lower layers?
  - For now I've just been using good old fashion `print('fart')` but I need to
    figure this out.

* [ ] **Figure out how exception handling fits into clean architecture**
  - From what I read online, each layer should catch exceptions and repackage
    them for higher layers to keep clean seperation.
  - For example, instead of letting database errors bubble up through the
    layers, catch them and re-raise as `SqlAlchemyRepositoryError`.

* [ ] **Remove cron stuff from ansible connector**
  - Now that we have the new user module service (soon to be refactored under
    clean arch), we can just use that to run cron commands as alt users more
    securely without having to become root.

* [ ] **This shouldn't be fatal, `install.sh` MAKE FIX!**
```
####### Installing Web-LGSM Ansible Connector...
####### Setting up Share Modules Dir...
mkdir: cannot create directory ‘/opt/web-lgsm/utils’: File exists
```

* [ ] **Fix the in app update!**
  - I think this is still broken which sucks.
  - You should be able to update the app from the web panel.

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

* [ ] **For install list do sort by alpha two columns header**
  - At the top of the install page, add some buttons to sort by alphabetical
    order for both columns.
  - Right now order is ascending by server short name.

* [ ] **Change sort order of game servers on main page**
  - User wants the ability to change the ordering of the GameServer items on
    the home page.
  - Either sort alphabetically or custom order.
  - [Related Issue](https://github.com/BlueSquare23/web-lgsm/issues/55)


### The Rest

* [ ] **Use controls.json for form validation & list**
  - I think that form is using a hardcoded list of valid controls for game
    servers so it blocks other controls for things like `force-update`.
  - I think this might hint at a bigger issue though and we should be doing
    more to detect available server controls. 
  - Related Issue: https://github.com/BlueSquare23/web-lgsm/issues/49

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

* [ ] **Clean up html and stray JS**
  - There's javascript in html templates still cause I'm lazy. Needs put in its
    own script fils(s) and linked.
  - Also just html in comments still and misc stuff like that.


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

