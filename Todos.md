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

* [ ] **Restructure application and build out proper API**
  - Ideally, the pages should just be an interface that communicate via rest-ish
    JSON to apps API endpoints.
  - Right now views routes / functions are handling waaayy tooo much logic. Whole
    apps functionality happens via views functions. All this should be
    happening via the app's API routes and just strung together by views logic.
  
* [ ] **Use Web Sockets for realtime communication**
  - The console for this thing is just some inefficient jquery contently making
    requests back to api endpoints. It works, but its a hacky mess. 
  - I want to transition the app to use web sockets for this communication
    instead.

* [ ] **Overhaul & Redesign test code**
  - [ ] Every single test should be idempotent (they're not rn).
  - [ ] No test should depend on any other test (they all depend on each other rn).
  - [ ] I need to learn more about how to actually fucking properly use pytest (rtfm).
  - [ ] Bonus points: If I can get some Selenium tests in here.

* [ ] **Improve overall design & documentation for project**
  - I want to actually properly try to design, document, and build out parts of
    this app. Full honest, I've never really done real software design before
    and this app up until this point (2025) was build with nothing but loose design 
    ideas and hopes and dreams.
  - This lack of design has fucked me and hampered the future development of
    this app. Oh well live and learn.
  - Major goal moving forward is to properly think, read, test, mockup, design,
    document, then build.

## Version 1.8.3 Todos

* [ ] **Fix whatever test(s) I just broke**
  - This commit e4f649805d99bdc6a76e001e46974ed348221e46 broke some tests.
  - Apparently, moving a bunch of install stuff to system level dirs is
    disruptive, whoda guessed it?

* [x] **Make App work via server_id's instead of server_name's**
  - Decided to make this a pre-req before getting into API routes, cause why
    keep writing new code that uses names instead of IDs.
  - But wow yeah this really turned into the metaphorical thread that unravels
    the whole sweater.
  - Several things in the install route need re-designed and I'm wonder if it
    might be better to dig even deeper and pull out even more of the rot at the
    core.
  - Still processing...

* [x] **Move API Routes into own file**
  - Unfortunately, this is not as trivial as copying and pasting the api route
    code into its own file because api routes use a shared global with view
    routes.
  - I know bad design. Time to repay some technical debt. Will position app to
    be way more betterer moving forward.

* [x] **Use real flask_restful module for spinning up api endpoints**
  - Allows me to use class based approach to define API endpoints.
  - Just gives me more tools to work with for properly handling data via api
    endpoints.
  - [x] Will require tweaking existing api endpoints to get them into classes,
    but shouldn't be too hard.

* [x] **Add builtin swagger docs for API**
  - API not incredibly useful yet on its own, but laying the groundwork.
  - As this projects more and more will be moved into the API and so this
    documentation will become more and more important so good to get a jump on
    it now.

* [x] **Turn Delete into its own API route**
  - Yeah this "page" doesn't render a template. Is basically already an api
    endpoint. Just needs formally converted into one.

* [x] **Fix multi game server delete to work via new api route**

* [x] **Make game server start just purge socket file name cache for that game server**
  - Right now its just a global cache purge which means all servers tmux socket
    name cache needs rebuilt after any one game server start.
    - This is slow.
  - If I write a function to just purge the socket name cache for that game
    server should speed things up a bit for other game servers.

* [ ] **Add controls redirect for game server name to new uuid for backward compat**
  - Basically, controls page used to work via names. I think there's a chance
    people still have links in their browsers and might still want to be able
    to go to `/controls?server=Minecraft` for example.
    - So going to just make that try to do a lookup & redirect to controls by
      UUID page for server.
    - Or something like that. Still thinking about it...

* [ ] **On first time loading server post install clear the install text.**
    - Aka when server install is marked finish, clear its entry from global
      servers dict. Then when someone enters the game server controls page for
      the first time they don't still see all the install blah output.
    - This is going to be difficult, because currently the ansible connector
      script is the thing that updates the `install_finished` field in the game
      server. However, the app state is what stores the ProcInfoVessel objects
      for installed game servers. So can't get the external script to update
      the apps state directly. Have to somehow trigger on that DB field being
      updated from within the app.

* [ ] **Make work for python 3.13**
  - I was silly and tried to put 3.13 in the tests at the end of this release
    and of course it failed lol. So screw it, v1.8 doesn't work with 3.13, will
    make it work soon.

## Version 1.8.4 Todos

* [ ] **Fix update mechanism... again**
  - I need to just mv existing to .bak and install fresh,
    - If fresh install goes awry move og back into place.
  - Install steps
    - Change to binary needs update or no needs update check.
    - Backup existing
    - Export DB to flat csv or json or something 
    - Install fresh
    - Import db and add any new fields

* [ ] **Make sure `web-lgsm.py --update` can deal with new folders owned as root.**
  - Might need to just put a little sudo chown back to the user line for those
    before running git pull or backing up etc.

* [ ] **Redesign test code!**
  - [ ] Make auto backup and git restore main.conf file.
  - [ ] Make each test idempotent, and make sure no tests are dependant on
    other tests. 
      - This is going to be quite the task because currently a lotta tests are
        dependant on the ones run before them. I'm bad at programming.
      - There's no real design being these tests, just lots of code piled up on
        itself & really needs cleaned up.

## Version 1.8.5 Todos

* [ ] **Add new page & API route(s) for Edit Game Server Info**
  - So far the only option for users to change game server information has been
    to delete the install and manually re-add it. Not a great solution.
  - I need to allow users to change their game server name, path, username,
    ssh-key, etc.
  - So there's need to be a new page and backend logic to enable this new
    feature.
  - This DB Model line set's install name to be unique:
    `install_name = db.Column(db.String(150), unique=True)`

* [ ] **Add new page & API route(s) for Restart/backup Scheduler.**
  - User suggested this feature and I think its a good one.
    - https://github.com/BlueSquare23/web-lgsm/issues/20
  - The idea here would be to create a simple web interface to wrap up adding
    crontab entries. Then the actual restarts or backups will just be handled
    by the lgsm game server cli script itself.
  - I've got all of the above to work through first but I do like this idea and
    want to add it in.

* [ ] **Add new page & API route(s) for export database information**
  - I want to allow users to export their database to csv or json or something
    for backup / manual update / migration purposes.

* [ ] **Add user action audit log feature + route for viewing**
  - Now that I have multiple users, when some user takes an action, I want to
    record who did what when to an audit log for later viewing by
    administrators in the web interface.
  - [ ] Need new database model to store audit log info.
  - [ ] Need new api routes to add info and remove info from audit log.

## Version 1.8.x Todos


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

* [ ] **Write some database tests that use the sqlite3 cli to test that data is
  actually making it into the db file.**
  - So just anywhere the app add stuff to the db, just verify with sqlite3
    commands that its in there.

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

* [ ] **Add option for anonymous usage statistics.**
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

* [ ] **Add more thorough tests over SSH.**
  - Setup a remote host with Minecraft on it.
  - Add flag to web-lgsm.py to do `--test_ssh`.
    - Don't run this as part of ci/cd.
    - Can't add a priv key so can't connect the ci tests to a remote host.
    - This would just be for me to run manually every so often to check
      everything over remote ssh is all good.


* [ ] **For install list do sort by alpha two columns header**
  - At the top of the install page, add some buttons to sort by alphabetical
    order for both columns.
  - Right now order is ascending by server short name.

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

