# Object Oriented Design Doc

## Overview

This application has thus far Not been build with any real Object Oriented
Design in mind. But we're changing that now and that's why this document
exists.

## Design Philosophies Used

As mentioned currently the design philosophy has been "no time to explain, grab
a cactus!" But we're now changing that.

I Think what we want to work toward here are Two main complimentary Design
Philosophies. But I still have to learn more about these approaches cause ngl,
don't really fully understand them yet.

### Clean Architecture

This is another one from Uncle Bob. The one is about the structure of our
classes and sorta layers of our application.

Its about dep management and separating concerns. We want to structure our code
so that the core business problem we're solving is independent from the
specific web framework or DB, etc. being used.

In sort its about what each layer of our code is doing.

See more about this under the High Level Design section below.

### Domain-Driven Design (DDD)

Domain Driven Design is about how do we lay out and model where our code lives
and group it related to the problem it is solving.

### Good-Ole MVC

Under this new arrangement the classic MVC becomes relegated to the
presentation layer only. Its becomes the outer most rim of the Clean Arch
onion. Then DDD defines the core and we use Clean Arch principals to pull it
all together.

### The Pieces 

Services - Coordinates multiple pieces (main business logic)

Managers - Manages the state of some resource (file, DB, API)

Routes - Edge layer, calls services, that call managers

Models - Data

---

Services should use Managers, but not the other way around. But tbh I'm still
not sure how exactly to best decouple the two. Right now just injecting deps
for managers that depend on services. But this is messy and a sign that further
restructuring is needed.

### Diagramming

We're going to use `mermaid` to make our class diagrams.

Specifically, we can use this pip package (`pymermaider`) to convert our
project's files into a class file for us automatically.

https://pypi.org/project/pymermaider/

https://github.com/diceroll123/pymermaider

I've already done this and created an initial [app.md](app.md) file to hold our
class diagram.

```bash
pymermaider . --extend-exclude "**/static/*"
```

NOTE: This project has not been built with a great deal of care toward OOD up
until this point (dev-v1.8.7, Nov. 2025). You see that fact reflected in the
current pretty flat and boring state of the projects class diagram.

### Where to go from here...

Only up. So far there's been little to no design. So as far as I see it, any
structure is better. But sill we should take care in building out new code.

## High Level Design

Watched this talk and it kinda helped.

[The Clean Architecture](https://youtu.be/DJtef410XaM)

Main idea is:

* IO (DB calls, requests, web stuff) should be the outer most ring around a

> "Imperative shell" that wraps and uses your "Functional Core"

So like the inner most modules shouldn't "do" anything. They just take in one
data structure and spit out another data structure.

Its sort of an inversion of the typical paradigm where methods abstract away
complexity and handle the messy business for you. Instead under this model,
methods simply take data structures and return data structures and on the outer
most layer is where the actual imperative "do" logic happens.

Example:

```python
# Outer Imperative Shell
def find_definition(word):
    url = build_url(word)
    data = requests.get(url).json()  # I/O
    return pluck_definition(data)

# Inner Functional Core
def build_url(word):
    q = 'define' + word
    url = 'http://api.duckduckgo.com/?'
    url += urlencode({'q': q, 'format': 'json'})

def pluck_definition(data):
    definition = data[u'Definition']
    if definition == u'':
        raise ValueError('that is not a word')
    return definition
```

So now we can test our `build_url` and `pluck_definitions` functions without
having to actually "do" anything, change any external state, etc. We just pass
data in and confirm it comes back out again correctly.

[Uncle Bob's - Clean Architecture](https://blog.cleancoder.com/uncle-bob/images/2012-08-13-the-clean-architecture/CleanArchitecture.jpg)

Now here's the thing, the app is not currently (Dec 2025) setup to work like
this, nor does it need to follow this like gospel. Its just guidelines for an
arch that is simple, extensible, and clean.



## I NEED TO RENAME AND REORGANIZE THINGS:

So I accidentally ended up naming everything a "Service." This is bad and I
already hate it. The word doesn't mean anything if everything's using it.

Both Deepseek and ChatGPT recommended I use a domain specific grouping.

### ChatGPT's Advice

Naming rules that prevent “Service Hell”

When creating a new class, ask one question:

“What would break if I replaced this with a stub?”

Business rules break → Service

Data consistency breaks → Manager

OS interaction breaks → Infrastructure

Implementation swap breaks → Adapter

Nothing breaks → Utility

If you can’t answer → it’s probably doing too much.

Final reassurance

What you did is not a mistake—it’s a normal phase:

    “Everything becomes a Service right before architecture starts to make sense.”

The fact that you’re uncomfortable with it means your instincts are good.

### Deepseek's Advice

Quick Rules of Thumb

    Use "Service" when: Coordinating multiple components, business workflow

    Use "Manager" when: Managing lifecycle/state of a specific resource

    Use "Handler" when: Processing specific requests/events

    Use "Repository" when: Direct data access

    Use "Client" when: External system communication

    Use "Helper/Util" when: Pure functions, utilities

### Main Problems

* [ ] **The utils.py file is bloated, unorganized, and untestable!**
  - Needs broken up into a bunch of different classes!

 [x] **Apps module code needs to be re-organized**
  - Take for example the `forms.py` file. Too many classes all in one file.
  - I might want to break that up into a directory of class files instead.
  - But in general, that code shouldn't be sprinkled with the main route, api,
    and models scripts. Needs to be seperated out carefully into its own dirs.

* [ ] **Module code needs separated and decoupled from app scripts**
  - Things are too tightly linked and interfaces need made standard and generic.
  - Need to embrace polymorphism.

### Breaking Up `utils.py`

Here's the rough plan for breaking up the very overloaded utils functions into
a new set of service layer classes. More about them below.

#### Grouping Our Current Functions

Server Operations Group (~8-10 functions)
```
    get_server_status, get_all_server_statuses, get_tmux_socket_name*, should_use_ssh
```

File Operations Group (~6-8 functions)
```
    read_cfg_file, write_cfg, download_cfg, find_cfg_paths, file operations over SSH
```

Command Execution Group (~5-7 functions)
```
    run_cmd_popen, process_popen_output, run_cmd_ssh, cancel_install
```

System & Monitoring Group (~4-6 functions)

```
    get_server_stats, get_network_stats, get_running_installs
```

SSH Infrastructure Group (~5-7 functions)

```
    _get_ssh_client, is_ssh_accessible, generate_ecdsa_ssh_keypair, get_ssh_key_file
```

Installation Management Group (~3-5 functions)

```
    clear_proc_info_post_install, installation-related functions
```

### Application Architecture

We're now using a layered architecture with a separation between presentation,
business logic, and data access layers.

* Presentation Layer: API & view route handlers
* Business Logic Layer: Service classes containing application logic
* Data Access Layer: Database operations abstracted within services

We're now using a _Service Layer_ to separate core application logic from the
backend functionality of specific app components.

For example, the CronService class is used to wrap up logic concerned with
accessing the database and invoking the ansible playbook to create or destroy
cronjobs on the system. In this way it interfaces with other service layer
classes, the database, and the core route code.

![Service Layer Diagram](ServiceLayerDiagram.png)

##### Directory Tree Structure

If you look at the version 1.8.6 release you'll see the app's code is still
mainly housed in just a few files. This was becoming too disorganized and a
limitation on growth. So instead, we've now broken things up a lot more.

```
app/
├── blueprints     # Route blueprints for api, auth, & main views
├── config         # ConfigManager class for handling main.conf ini files (TODO: Turn into service layer class)
├── database.db    # Sqlite database file
├── extensions.py  # Flask extension specific stuff
├── forms          # Flask-Wtf Wtforms classes (user input handling & validation)
├── __init__.py    # App factory for producing app
├── models         # Flask-Sqlalchemy database model classes
├── paths.py       # Static hardcoded path vars (needs moved into utils)
├── services       # Service layer classes
├── static         # Static CSS, Javascript, & Images
├── templates      # Jinja2 html template files
└── utils          # Non-dependant generic helpers
```

### Service Layer Classes (Done)

* `CommandExecService` - Interface for command line operations (via local shell, or ssh via dep inversion).
* `BlocklistService` - Simple in memory fixed size IP block list for basic brute force login protection.
* `ControlsService` - Interface for fetching dynamic GameServer specific controls.
* `CronService` - Interface for interacting with crontab editing and app jobs data.
* `ProcInfoService` - Singleton class for sharing `proc_info` objects between route code and other services.

### Service Layer Classes (Needed)

* `GameServerService` - GameServer specific service for finding additional info about GameServer objects.
* `FileService` - Service for interacting with files on the file system (or over ssh via dep inversion).
* `MonitoringService` - Interface for checking system stats for front page charts.
* `InstallService` - Interface for dealing with installing related stuff (might not need this one yet).

I'm still not totally sure how I'm going to do the FileService and CommandExec
service. I'd like to use dependency inversion to pass both of those an
interface that is either local or remote or docker and have it just do the
necessary thing.

### Service Container

We're passing the individual services through a `ServicesContainer` object for
ease of use. (Pseudo code below, not implemented yet...)

```python3
# services/__init__.py
from .server_service import ServerService
from .file_service import FileService
from .command_service import CommandService
from .ssh_service import SSHService
from .system_service import SystemService

# Simple service container
class ServiceContainer:
    def __init__(self):
        self.ssh = SSHService()
        self.command = CommandService() 
        self.file = FileService(self.ssh)
        self.server = ServerService(self.command, self.file)
        self.system = SystemService()

services = ServiceContainer()
```


### How CommandExecService Works

The `CommandExecService` class acts as a universal interface for running
commands via the app. It takes advantage of dependency inversion to run both
local commands and commands over ssh.

The way this works is we create a `BaseCommandExecutor` class that both
`SshCommandExecutor` and `LocalCommandExecutor` inherit from. Then when the
`CommandExecService`, `run_command` method is called, it will select and use
the appropriate executor.



### UserModuleService

The user module service is a facade. It runs user module scripts which are kept
in the `app/utils/shared` directory.

These "scripts" can be invoked by the UserModuleService in two ways:

1. These modules are directly imported and run (used for same user game servers).
2. These modules are run through shared cli.py via sudo -u username (used for non-same user game servers).

This service provides a uniform interface running shared module code, that is
not dependant on the user the code needs to be invoked as.

For example, see the `app/utils/shared/find_cfg_paths.py` shared module file.
If a game server is installed under the same username as the web app then we
can simply import the `find_cfg_paths` function from that file and run it.

However, if the game server is installed under some other user, then we'll need
to run that code via `sudo -u otheruser python -m shared.cli` in order to get
results back.

The whole point is that the client calling this wrapper does need to care if
its same user or some other user. The results returned should be the same
either way.


### CfgManagerService

This class makes use of the UserModuleService in order to fetch the location of
`cfg_files`. Its really just another wrapper to make it easy for route code to
fetch this info and not have to care about if server is remote, local
same-user, or local non-same-user.




