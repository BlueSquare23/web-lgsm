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

* [x] **Overhaul & Redesign test code**
  - [x] Every single test should be idempotent (they're not rn).
  - [x] No test should depend on any other test (they all depend on each other rn).
  - [x] I need to learn more about how to actually fucking properly use pytest (rtfm).
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


## Version 1.8.4 Todos

* [x] **Fix core update mechanism... again**
  - Still needs thoroughly tested but think I mostly got it.
  - Big key to updates moving forward is the Flask-Migrate (Alembic) database change system.

* [x] **Make sure `web-lgsm.py --update` can deal with new folders owned as root.**
  - Yeah the update mechanism

* [x] **Redesign test code!**
  - [x] Refactor big test and conftest.py functions.
  - [x] Make auto backup and git restore main.conf file.
  - [x] Make each test idempotent, and make sure no tests are dependant on
    other tests. 
      - This is going to be quite the task because currently a lotta tests are
        dependant on the ones run before them. I'm bad at programming.
      - There's no real design being these tests, just lots of code piled up on
        itself & really needs cleaned up.

* [x] **Fix install.sh --docker for Debian**
  - User noticed the issue:
    https://github.com/BlueSquare23/web-lgsm/issues/41
  - Just need to make docker install case on debian vs ubuntu.

* [x] **Add CSRF protection using Flask-WTF**
  - I did not realize until today that flask doesn't do anything to prevent
    CSRF natively.
    - Same Site is set to None and its totally possible to trick someone into
      making POSTs to forms.
  - Forms to do:
    - [x] Add
    - [x] Settings
    - [x] Login
    - [x] Setup
    - [x] Controls
    - [x] Edit
    - [x] Home: Doesn't really need one, not a real form that gets submitted to the backend. Just a button that triggers js to make fetch reqs to api /delete.
    - [x] Install
    - [x] Edit Users
  - Resources:
    - https://flask-wtf.readthedocs.io/en/1.0.x/quickstart/
    - https://wtforms.readthedocs.io/en/2.3.x/fields/
    - https://flask-wtf.readthedocs.io/en/0.15.x/form/#secure-form
    - https://www.geeksforgeeks.org/flask-wtf-explained-how-to-use-it/
    - I might want to use this to handle file uploads one day too.

* [ ] **Spend some time fleshing out new singleton code & integrating into app**
  - I added this, I got it working, I somewhat tested it. However, I have not
    gotten around to refactoring fundamental parts of the app to use it yet.
    - Now seems like a good time to do that because old tests have been brought
      into the present and updated, however new tests for this have not been
      added yet.
    - I was so busy with adjusting from server name -> id that it kinda ate up
      most of the last releases time. 
  - Make utils functions work via IDs and access objects from global dict,
    instead of being passed the whole object directly as arg. 
  - Note to self, not an excuse to run wild and get distracted refactoring
    every little thing. Stay on task! Just update core functions to use new
    code.

* [ ] **Continue fixing up tests**
  1. As much as I hate to admit it, the coverage reports are kinda useful for
    spotting things that I have little to no testing for.
    - A lot of this stuff is newer stuff, I added but never got around to
      testing, cause was going to do some overhaul on the tests anyways.
    - [ ] Look at recent coverage reports to find things that lack tests and
      write some more tests!
  2. There are a number of existing tests that are pretty weak, kinda don't
    really test what they're supposed to test well. 
    - I left myself a bunch of TODOs in comments.
    - [ ] Refactor existing _"weak"_ tests to improve tactility (aka better
      grip on subject matter being tested) & robustness (aka no race
      conditionss, cheats & other hacks to fudge it so tests pass).
  3. [ ] For Assert step, CHECK MORE STUFF VIA THE DB DIRECTLY!!!
    - I really need to be taking an action, then checking the DB.
    - I'm checking a lot of responses from the outside to make sure they're as
      expected. However I'm not really checking directly in the DB itself to
      make sure things are all good.
    - But I can do that, so I should be doing that. Oh well always more things
      to do than time to do them.

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


* [ ] **Make work for python 3.13**
  - I was silly and tried to put 3.13 in the tests at the end of this release
    and of course it failed lol. So screw it, v1.8 doesn't work with 3.13, will
    make it work soon.

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

