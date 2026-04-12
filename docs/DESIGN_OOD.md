# Object Oriented Design

## Overview

This application has thus far Not been build with any real Object Oriented
Design in mind. But we're changing that now and that's why this document
exists.

## Design Philosophies Used

As mentioned currently the design philosophy has been "no time to explain, grab
a cactus!" But we're now changing that.

### Clean Architecture

This is another one from Uncle Bob. The one is about the structure of our
classes and sorta layers of our application.

Its about dep management and separating concerns. We want to structure our code
so that the core business problem we're solving is independent from the
specific web framework or DB, etc. being used.

In sort its about what each layer of our code is doing.

See more about this in the [Architecture.md](Architecture.md) file.

## Tooling

### Class Diagrams

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

### Dependency Graphing

We're using a tool called `tach` to auto generate some dependency graphs to
help us better understand existing relationships.

https://docs.gauge.sh/

https://docs.gauge.sh/getting-started/introduction/#commands

How to generate a tach graph.

```
# Install tach
sudo -E /opt/web-lgsm/bin/python3 -m pip install tach

# Tach init, then select everything
tach init

# Run tach sync to "set boundries" (no idea what that means but they tell you to do it)
tach sync

# Generate local graph
tach show

# Display graph in tach webui
tach show --web
```

I don't know how long these links stay live for but here's one I generated
recently.

https://app.gauge.sh/show?uid=6821ab70-fef5-48c6-bffe-1d5f4f3b6a67

### Where to go from here...

Only up. So far there's been little to no design. So as far as I see it, any
structure is better. But sill we should take care in building out new code.

## Misc Other Notes

### Main Problems

* [ ] **The utils.py file is bloated, unorganized, and untestable!**
  - Needs broken up into a bunch of different classes!
  - [x] This is 80% done, but now overall arch needs established, see clean arch notes above.

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


