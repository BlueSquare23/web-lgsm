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

### Good-Ole MVC

Under this new arrangement the classic MVC becomes relegated to the
presentation layer only. Its becomes the outer most rim of the Clean Arch
onion. Then Clean Arch defines the core and helps pull it all together.

### The Layers (the goal)

A pragmatic Clean Architecture with 4 layers:

```
┌──────────────────────────────┐
│        Interface Layer       │  (Flask, blueprints, forms)
├──────────────────────────────┤
│       Application Layer      │  (Use cases)
├──────────────────────────────┤
│          Domain Layer        │  (Entities + interfaces)
├──────────────────────────────┤
│       Infrastructure Layer   │  (DB, filesystem, tmux, OS, etc)
└──────────────────────────────┘
```

### A Slight Dirty Arch (Right Now)

I do not really want to rewrite and restructure absolutely everything just for
the sake of "purity." Like end of the day, 99.9999% of people do not care about
the app's architecture.

So what we need is to borrow some ideas from Clean Arch to help clean
things up. But what exactly?

Well idea No.1 is:

#### Separation of Concerns / Dependency Graph

A good software application is like an ogre. Here's our apps current dependency graph.

```
     v-----Controllers (aka Routes) 
     M       |       |    
     o       |       v    
     d <-----+-----Validators (aka WTForms) 
     e       |       |    
     l       v       v    
     s <-----Services / Managers

```

The astute among you may realize that a bit of a mess.

Everything is talking to the DB. Controllers and services are still tightly
coupled. The layers are not clearly defined and its begging to create more
circular import problems.

What I'd like it to be:

```
  Controllers (aka Routes)
          |
          v
  Use Cases (Application)
          |
          v
  Entities (Domain)
          ^
          |
  Infrastructure (DB, filesystem, tmux, OS, etc)
```

### The Only Rule That Matters

> Dependencies always point inward.

```
interface -> application -> domain
infrastructure -> domain
```

Domain depends on nothing.

Application depends only on domain.

Interface depends on application (never on infrastructure directly).

Infrastructure depends only on domain (to implement interfaces).

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

### Everything's A Service

> [!NOTE]
> I NEED TO RENAME AND REORGANIZE THINGS:

So I accidentally ended up naming everything a "Service." This is bad and I
already hate it. The word doesn't mean anything if everything's using it.

I need to break things up more and looks like clean arch is the way to do it.


## The Road to Cleaning This All Up!

Taking the current app's structure and converting it to a clean architecture
isn't going to happen over night.

Things will need to be Broken apart and re-assembled using ports and adapters.
We will need to figure out application usecases, domain entities, and
repositories from our existing code. I suspect much of our existing code is
going to end up in the infrastructure dir.

But what really matters here for clean arch is a clean separation of the layers.

Our "controller" (aka blueprints routes) get's flattened out to become our
"Interface" layer. The interface layer depends only on the application layer
(previously our service layer). Our application layer we define use cases.
Those use cases depend on our domain layer entities and interfaces. And then at
the very bottom is our infrastructure layer that depends only on domain
entities.

## A Transition Plan

We're going to look at the example of how I converted the app's Audit stuff to
use a clean arch setup. This will serve as a useful template for converting other
more complex features in the future.

This is a high level overview of the transition roadmap. For more details on
this particular conversion, see the commit [COMMIT_HASH_HERE] and [detailed
breakdown linked here](./more_arch_notes.md).

Basically, here's the process.

1. Create new domain entity called Audit in `app/domain/entities/audit.py`
2. Define a blank repository interface in `app/domain/repositories/audit_repo.py`
3. Move SQLAlchemy Model to `app/infrastructure/persistence/models/audit_model.py` and remove event listener.
4. Create new infrastructure repo to interface with DB model in `app/infrastructure/persistence/audit_repository.py`
5. Create some new use cases for `log_event.py` and `list_audit_logs.py` in `app/application/use_cases/audit/`
6. Tweak audit blueprint to remove old calls to old audit DB model
7. Create new `app/container.py` to wrap up new audit usecases and repository
9. Replace old `audit_log_event` func calls with new `container.log_audit_event().execute()` calls

What this accomplishes:

* It moves access to the Sqlite model into the `SqlAlchemyAuditRepository`
  - That's the only layer that talks directly to the DB now (for AuditModel).
* Separated DB representation for Application Entity.
  - Now the DB model is not the same thing of that entity object we work with in the app.
* Created repository interfaces for passing data from entity to persistent DB.
* Introduced use cases to hold business rules.
  - In audit case allowed me to move rules out of db model upward into application layer.
* Defined a clear unidirectional dependingly graph.
  - Dependencies all point inward.

## Misc Other Notes

### Main Problems

* [ ] **The utils.py file is bloated, unorganized, and untestable!**
  - Needs broken up into a bunch of different classes!
  - [x] This is 80% done, but now overall arch needs established, see clean arch notes above.

 [x] **Apps module code needs to be re-organized**
  - Take for example the `forms.py` file. Too many classes all in one file.
  - I might want to break that up into a directory of class files instead.
  - But in general, that code shouldn't be sprinkled with the main route, api,
    and models scripts. Needs to be seperated out carefully into its own dirs.

* [ ] **Module code needs separated and decoupled from app scripts**
  - Things are too tightly linked and interfaces need made standard and generic.
  - Need to embrace polymorphism.

### Additional Problems

* [ ] **We're using Flask Sqlalchemy, so ORM is dependant on framework**
  - Since our ORM is dependant on our web framework, we're kinda locked into
    the existing database classes and using the ORM to access them.
  - This is fine for the timebeing, but if we do want to eventually lean more
    into DDD (with model class simply becoming a DTO and each domain having
    their own entity objects) then we'll be forced to abandon flask sqlalchemy.
  - Or we house the ORM calls in a Repositories, but that just seems silly.

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

### Current Messy Application Architecture

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

> [!NOTE]
> THIS IS ALL SUBJECT TO CHANGE SOON!

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

Second thought, I might abandon this idea. We'll see if it fits in after clean
arch re-shuffling. Good thing I never got around to adding it!

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




