## Version 1.8.0 Todos

### v1.8.0 Pt 2.5.  Add Remote Admin Over SSH Support

* [ ] **Add ability to admin remote game server(s) over SSH through web portal.**
  - The idea here would be to allow the web-lgsm interface running on serverA
    to connect to another machine on serverB and run game server admin commands
    (stop, start, restart, etc.).
    - Basically, exactly the same stuff as for local install's it would just
      run the command over ssh instead.
  - Involves:
    - [x] Make main controls for local installs owned by other users work over ssh.
    - [x] Get Send command working over SSH.
      - Just some backend logic needs written.
    - [x] Get live console output working over SSH.
      - [x] Rebuild watch code with frontend ajax instead.
        - I've decided to finally ditch the long running `watch` process as a
          simulacrum of a running console.
        - Instead, I've tweaked the tmux capture pane cmd to get all text from
          the session.
        - I'm going to make a new POST api route, /api/refresh_console.
          - The /controls page console command will, send a post (aka trigger
            an ssh connection, to tmux capture the output).
          - Then once that returns ok, the `updateTerminal()` js will run
            fetching the latest output from /api/cmd-output.
          - This way don't need to do whole page reload.
          - Just some js for when in console mode, post to refresh api, fetch
            output api.
    - [x] Figure out delete over ssh.
      - Right now delete is run via sudo ansible connector because it can also
        delete the other users.
      - I might keep that for local installs, but for remote just remove files.
      - Maybe I should add a toggle / config setting for "cleanup system user
        on delete" or something like that.
    - [x] Figure out update config files over SSH.
      - I was going to put this off for a future release, but then there's no
        good way to do edit cfg files for game servers installed as other
        system users.
      - I don't want to run that through the ansible connector script.
        - Once again should only really elevate privs when absolutely
          necessary.
      - Problem is this might then interfere with my vision for the below
        bullet point.
    - [ ] Write `ssh_connector.sh` shell script. Basically if I want to limit
      access to multiple commands over ssh I need to do something like this:
      - https://serverfault.com/questions/749474/ssh-authorized-keys-command-option-multiple-commands
      - I think doing this in bash is probably safe enough.
        - Will just have to validate cmds are legit.
        - Will cross `send` command bridge when we come to it. 
  - Things I'm not going to do:
    - Defer install game server over ssh till next release.
      - More code than I wanna write right now (already a lot in this release)!

* [ ] **Fix tests broken by recent changes.**
  - I don't even know what all is broken yet, that's next step is run em and
    start fixing them after above changes are done.

* [ ] **Write new tests for recent changes.**
  - Includes:
    - [ ] Test add game server `install_type` remote.
      - Will use some dummy hostname or IP that's open on ssh I got plenty of
        hosts I can pick from.
      - Also can't really run commands on a dummy remote but should basically
        be no different from running commands as a different system user over
        ssh. So probably going to say that's good enough for this release.

### v1.8.0 Pt 3. Dockerize and Shine
---

* [ ] **Add Support for game servers in containers!**
  - My thoughts are in this case its much like the add but just for docker
    containers.
    - So users would've already setup these containers ahead of time
      themselves, I'm just allowing users to add their existing lgsm docker
      containers to the web interface.
    - Aka instead of running a command like this via the shell:
      `./csgoserver details`
    - The app will just be running a command like this via the shell:
      `docker exec -it --user linuxgsm csgoserver ./csgoserver details`
  - [x] To do this I think I'll need a toggle on the add page for "game server is
    in a container".
  - [x] I'll also need another field in the GameServer model for "install_type"
    and set it to docker.
    - The thing is I don't want to manage containers, I don't want to stop,
      start, restart containers themselves with my app. Use Portainer or
      something if you want that.
    - Instead my app's just going to check if the game server container is
      running and if so you can run commands for it through the web interface.

* [ ] **Add docs for docker changes.**

* [ ] **Manually run tests against new changes in container.**
  - If I edit the Dockerfile manually and make the ENTRYPOINT `web-lgsm.py
    --test_full` then it should build and run all project tests inside of the
    container.
  - I don't have a way to automatically hook this into github actions ci yet so
    making a note here to just run them by hand.
  - I mean its kinda silly cause the actions themself are in a container so
    afaic same thing.

* [ ] **Apply autoformatting via `black`.**

### v1.8.0 Pt 4. The Rest...
---

* [ ] **Add search bar to install page.**
  - User brought up in [this Github Issue](https://github.com/BlueSquare23/web-lgsm/issues/27).
  - I can do this all in JS on top of the existing page.

* [ ] **Make main.conf option & settings page toggle for: 'convert carriage returns to newlines'**
  - This is the old style and some people might like the ability to switch back.
  - Now with xterm.js I can take advantage of proper carriage return chars \r
    so I'm now using those, might as well. Makes things look a little more
    anitmated.
  - But some folks might still prefer the old style and I think it should be an
    easy enough fix to add the \r -> \n conversion back in to the backend ssh
    wrap function as an optional setting.
  - Write a test for this new settings option.

* [ ] **Add show_stderr main.conf option to suppress stderr_messages.**
  - Not everything that comes out of stderr is fatal.

* [ ] **Make config editor work for game servers owned by other system users.**
  - [ ] Think I'll have to re-write / add-to the write new config data logic.
  - Right now it just writes to disk as the current user.
  - [ ] Instead I think I'll have it send the data over SSH (somehow) and chown
    it to the new user.
  - Will be a little more complicated but shouldn't be too crazy.

* [ ] **Put more error handling & set default values for main.conf parameters in
  code.**
  - The idea here is if some user doesn't have some parameter set in their
    main.conf, or if their main.conf is totally mangled or something, then the
    app shouldn't fail catastrophically, which I think it kinda does rn.

* [ ] **Make sure `web-lgsm.py --update` can deal with new folders owned as root.**
  - Might need to just put a little sudo chown back to the user line for those
    before running git pull or backing up etc.

* [ ] **Allow multiple auto installs of same game server as new user, just increment
  the name.**
  - So first mcserver install would just be mcserver but then a second one the
    user would be mcserver2, mcserver3, etc.

* [ ] **Standardize greens!**
  - I'm using too many different shades of green all over.
  - ![3 different greens](https://johnlradford.io/static/img/3differentgreens.png)
  - Make them all the same.

* [ ] **Make game server name editable.**
  - This DB Model line set's install name to be unique:
    `install_name = db.Column(db.String(150), unique=True)`

* [ ] **Make install_path an optional main.conf parameter.**
  - By default I want to set this to just `/home/<user>/<server_name>`.
  - But then allow people to put it where ever for their own purposes.
  - Write tests for this.

* [ ] **Make install.sh setup npm pkgs at the end.**
  - I'm using xterm.js and a plugin for them that can only be installed via
    npm.

* [ ] **Add support for Ubuntu 24.04.**
  - Ubuntu 24.04 is out now too. Can add that to `.github/workflows/test.yml`
    too.

### v1.8.0 Pt 5. QA...
---

* [ ] **Thorough code review process.**
  - [ ] Pt 1. Identify targets for refactoring. Just find and tag for later things
    that need refactored.
    - Review changes for new features:
      - [ ] Backend ansible sudoers passwordless changes
      - [ ] Multi web interface user changes
      - [ ] Running in a container
      - [ ] Managing game servers in containers
    - [ ] Do a high level overview of whole project, looking function by function
      for things that stick out as stinky...
      - If there are some really messy or iffy sections of the code where I
        hacked something together that really needed more thought, now is the
        time to try to identify those things.
      - Not fixing or changing anything just yet. Just want to review what I
        have and where its weak to better get an idea of how to fix it later.
  - [ ] Pt 2. Address targets for refactoring.
    - I suspect some of them will be easy fixes and some more involved.
    - Really big refactors will probably get pushed off till next release.

* **List of Targets for refactoring:**
  - [ ] All the overhead comments for functions n'@ can be turned into under
    hanging docstring to make the more _pythonic_.
  - [ ] Remove stupid line breaks with \.
    - Let black handle formatting.
    - Again another one of these things that I don't really know why I did
      that. Guess I was trying to keep things at 80 columns like these lines. Even though that's arbitrary and we all have screens nowadays that are more than 80 columns wide.
      - 100% am going to accidentally justify the above line at some point bet.
    - At least in this case changes are not destructive at all.
    - Might even help me identify some places where things can be reduced /
      refactored more.
  - [ ] Make sections for GET and POST explicit ifs. Right now I'm relying on a lot
    of mixed code where like stuff for GET req's happens both above and below
    the POST if block.
    - So that's just like confusing to read and needs cleaned up.
    - I think I understand what I was trying todo and be efficient and not put
      lines twice if I didn't have to.
      - But I've grown as a programmer since then and now no longer care.

* [ ] **Apply autoformatting via `black`.**

* [ ] **MANUAL QA TESTING.**
  - [ ] Going to try to bribe my friends with pizza and or fine lettuces to go
    through and make sure its doing the needful.
  - [ ] Look for bugs, try to break it, suggest improvements.
    - Small bugs if found, can be fixed.
    - Big bugs if found, can be hackily dealt with, then properly fixed in next
      release.
    - Feature suggestions can go into the next release.

* [ ] **Add new docs & Fix existing docs.**
  - A decent amount of review needs done here, I haven't even begun to look but
    probs going to be a lot.

* [ ] **Fix up Readme.**
  - [ ] Update Readme gifs with newest look of interface.
  - [ ] Add contribute section pointing users to submitting an issue or submitting a
    pull request.
    - I have the community docs for this now.


## Version 1.9.0 Todos

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

* [ ] **Add Restart/backup Scheduler.**
  - User suggested this feature and I think its a good one.
    - https://github.com/BlueSquare23/web-lgsm/issues/20
  - The idea here would be to create a simple web interface to wrap up adding
    crontab entries. Then the actual restarts or backups will just be handled
    by the lgsm game server cli script itself.
  - I've got all of the above to work through first but I do like this idea and
    want to add it in.
  - Just a matter of time until I can get to it.

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

