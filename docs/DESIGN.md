# Design Document: Web-LGSM

## 1. Introduction
- **Purpose**: The Web-LGSM is a simple web interface for managing LGSM game servers.
- **Scope**: This document covers the high-level architecture and specific components of the web-lgsm.
- **Audience**: This document is intended for developers, contributors, and maintainers. However, general users may find it interesting as well.

---

## 2. Overview
- **Project Goals**: The goal of this project is to provide an easy to install, maintain, and use web interface for managing LGSM game servers (optionally within containers) on a single machine or across multiple servers.
- **Technology Stack/Dependencies**:
  * Language: [Python 3](https://www.python.org/)
  * Web Framework: [Flask](https://palletsprojects.com/p/flask/)
  * Database: [SQLite](https://www.sqlite.org/index.html)
  * ORM: [SQLAlchemy](https://www.sqlalchemy.org/)
  * CSS Framework: [Bootstrap 5](https://getbootstrap.com/docs/5.0/getting-started/introduction/)
  * JavaScript: [jQuery ajax](https://api.jquery.com/jQuery.ajax/)
  * Web Terminal: [Xterm.js](https://xtermjs.org/)
  * SSH Client [Paramiko](https://www.paramiko.org/)
  * Testing: [Pytest](https://docs.pytest.org/)
  * Automation: [Ansible](https://www.ansible.com/)
  * Web Server: [Gunicorn](https://gunicorn.org/)

---

## 3. Architecture
- **High-Level Diagram**:
![Design Diagram](images/design_diagram.png)
- **Components**:
  * `web-lgsm.py`: Main project init script. Takes care of starting, stopping, restarting the main gunicorn server. But can also be used to run pytests, updating the app, changing passwords, and more. Main point of entry script for the project.
  * `Flask App`: The main flask application. Basic MVC architecture. Game server and user info is stored in the SQLite db, config options in main.conf. Utilized external ansible connector for game server install & delete.
  * `Ansible Connector`: Middleware script for running ansible playbooks (for game server install & delete) with elevated privileges. Playbooks set up new system user, sets up ssh to new user, & installs game server.
  * `Models`: DB models used to store info about users and connected game server installs. I'm using Flask's SQLAlchemy ORM to interact with the database.
  * `Objects`: As of right now, this app is not very OOP. Mainly I'm just using one `ProcInfoVessel` class to create objects for storing output from commands. I'd like to make this app more object oriented in the future, but everything takes time.
  * `main.conf`: The main configuration file for storing settings relating to aesthetic & control features for the flask app. The settings page updates this file directly.

---

## 4. Detailed Design
- **Routes/Endpoints**:
![Routes Diagram](images/routes.png)
  * Auth Routes
    - `/login`: Handles authentication to web portal, can't access any other pages until logged in.
    - `/setup`: Web-lgsm setup page, becomes inaccessible after initial user creation.
    - `/logout`: Handles logging users out of web interface.
    - `/edit_users`: Handles creating, modifying, & deleting additional web interface users.
  * Views
    - `/`: Alias for home page.
    - `/home`: Application home page index, contains links to game servers and live web-lgsm system cpu, mem, disk, net stats view.
    - `/controls`: Controls page for individual game servers. Holds start,stop,restart,etc. buttons, live console, and links to config editor.
    - `/install`: Install new game servers page. Contains a list of available LGSM game server titles that can be installed with the click of a button!
    - `/settings`: Main settings page for application settings. Settings are stored in and map to values in the `main.conf` file. See `docs/config_options.md` for full list of config options.
    - `/about`: Basic about and credits page, nothing fancy.
    - `/add`: Page for adding additional already installed LGSM instances to the web interface. Can add locally installed game servers, game servers installed on remote servers, and game servers installed within docker containers.
    - `/edit`: Game server config file editor page. If enabled, allows users to edit specific game server files through the web interface.
  * API:
    - `/api/delete`: API route for handling game server delete requests. 
    - `/api/update-console`: Handles running the underlying cmd for dumping tmux session live console output and returning it as a json object. (this is a hack and is bad!)
    - `/api/server-status`: Handles returning live server status json used by home page cpu, mem, disk, net charts.
    - `/api/cmd-output`: Handles running cmds and returning json output for all non-live console output cmds. (live console is weird, needs it own route)
- **Models**: Describe the database models (if using SQLAlchemy or another ORM).
- **Services**: Explain any backend services or business logic.
- **Templates/Views**: If using Flask templates, describe how they are structured.
- **Static Files**: Explain how static files (CSS, JS, images) are organized and used.

---

## 5. Design Decisions
- **Rationale**: Explain why certain design choices were made (e.g., why Flask, why a specific database, etc.).
- **Trade-offs**: Discuss any trade-offs or compromises in the design.
- **Alternatives Considered**: Mention any alternative approaches that were considered and why they were not chosen.

---

## 6. API Documentation
- Builtin Swagger documentation under `https://your_web_lgsm_url/docs`.
![Swagger Docs](images/swagger_docs.gif)

---

## 7. Configuration
- **Environment Variables**: List and describe the required environment variables.
- **Configuration Files**: Explain any configuration files and their structure.

---

## 8. Deployment
- **Deployment Process**: Describe how the application is deployed (e.g., using Docker, Heroku, etc.).
- **CI/CD**: If applicable, explain any continuous integration/continuous deployment pipelines.

---

## 9. Testing
- **Testing Strategy**: Practical > Coverage

This project is tested using `pytest`.

The main goal of this projects tests are practically test if shit is working or
not. I have not put a big focus on code coverage. Toward this end you'll find
that the bulk of the tests are functional, input output response test of how the
app's routes behave with scant unit tests.

We're now trying to use the _"Arrange-Act-Assert (AAA)"_ Pattern when creating
the tests. Below cribbed directly from automationpanda.com.

The Pattern

Arrange-Act-Assert is a great way to structure test cases. It prescribes an
order of operations:

* Arrange inputs and targets. Arrange steps should set up the test case. Does
  the test require any objects or special settings? Does it need to prep a
  database? Does it need to log into a web app? Handle all of these operations
  at the start of the test.

* Act on the target behavior. Act steps should cover the main thing to be
  tested. This could be calling a function or method, calling a REST API, or
  interacting with a web page. Keep actions focused on the target behavior.

* Assert expected outcomes. Act steps should elicit some sort of response.
  Assert steps verify the goodness or badness of that response. Sometimes,
  assertions are as simple as checking numeric or string values. Other times,
  they may require checking multiple facets of a system. Assertions will
  ultimately determine if the test passes or fails.

[Arrange-Act-Assert (AAA) Pattern Explained](https://automationpanda.com/2020/07/07/arrange-act-assert-a-pattern-for-writing-good-tests/)

### Tests Components & Structure

Here's the basic test dirs structure:

```
tests/
├── conftest.py
├── functional
│   ├── test_auth.py
│   ├── test_views.py
│   └── test_web-lgsm.py
├── game_servers.py
├── test_data
│   ├── common.cfg
│   └── Mockcraft
│       ├── linuxgsm.sh
│       └── mcserver
├── test_vars.json
└── unit
    ├── test_models.py
    └── test_utils.py
```

We have a few things going on here: 

* The `conftest.py` file. This is where the test setup and teardown happen.

* The `functional` holds our functional tests. These use the client and other
  pytest fixtures setup by the `conftest.py` to test the apps various routes
  and to test the `web-lgsm.py` itself.

* The `game_servers.py`: Loads some json from static file for tests (just a lil util).

* The `test_data` dir holds the fake _"Mockcraft"_ install (not a full game
  server install, just the bare files for mocking).

* The `test_vars.json` file holds some static data used for testing stuff. Why
  is this not in the apps json folder? `¯\_(ツ)_/¯`

* The `unit` dir holds the projects straight unit tests of utils functions and
  the apps models. These could really used expanded and made more through, but
  ya know time...

Basically, the `conftest.py` has a bunch of pytest fixture functions in it
that are used to do the setup & teardown (aka the Arrange step) for tests to
ensure _idempotency_ and _independence_. Then the actual `test_` files
themselves are where the Act and Assert steps come in.

* Independence: Meaning no test relies on any other test to work working.

* Idempotency: Meaning no test should leave artifacts that affect overall
  state. Everything should be setup fresh for each test and nothing should be
  left behind that affects another test.

Both of these things together mean that any one test should be able to be run
in isolation and be self contained, and its passing or failing should not
affect any other tests.

### Coverage

Code coverage reports generated with [`coverage`](https://coverage.readthedocs.io/en/7.8.0/).

* Run pytests with coverage:

```
» coverage run -m pytest -v
```

```
# Generated: Sat Apr 19 03:49:24 PM EDT 2025
» coverage report
Name                                Stmts   Miss  Cover
-------------------------------------------------------
app/__init__.py                        57      4    93%
app/api.py                            122     34    72%
app/auth.py                           195     20    90%
app/cmd_descriptor.py                   9      1    89%
app/models.py                          33      1    97%
app/proc_info_vessel.py                15      0   100%
app/processes_global.py                15      0   100%
app/utils.py                          746    250    66%
app/views.py                          532    132    75%
tests/conftest.py                     113     17    85%
tests/functional/test_auth.py         205      2    99%
tests/functional/test_views.py        681     15    98%
tests/functional/test_web-lgsm.py      29      0   100%
tests/game_servers.py                   5      0   100%
tests/unit/test_models.py              26      0   100%
tests/unit/test_utils.py              127      8    94%
-------------------------------------------------------
TOTAL                                2910    484    83%
```
---

## 10. Database Upgrades
- **Flask-Migrate (Aka Alembic)**: Alembic is a lightweight database migration
  tool for usage with the SQLAlchemy Database Toolkit for Python.

We're using the Flask version of Alembic called `Flask-Migrate`.

* Initial database revision tracking for DB. (This only ever needs done once).

```
flask --app app:main db init
```

* Add a new field to a `models.py` file.

```
img_path = db.Column(db.String(150))  # New field
```

* Create a new migration: This will generate a new file in `migrations/versions/` for this change.

```
flask --app app:main db migrate -m "add img_path to User model"
Root logger level: WARNING
 * Database Loaded!
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added column 'user.img_path'
  Generating /home/blue/Projects/web-lgsm/migrations/versions/d2829b640c78_add_img_path_to_user_model.py ...  done
```

* Run the migration to apply the changes to the DB.

```
flask --app app:main db upgrade
Root logger level: WARNING
 * Database Loaded!
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> d2829b640c78, add img_path to User model
```

* See current revision:
```
flask --app app:main db current
Root logger level: WARNING
 * Database Loaded!
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
d2829b640c78 (head)
```

* See revision history:
```
flask --app app:main db history
Root logger level: WARNING
 * Database Loaded!
<base> -> d2829b640c78 (head), add img_path to User model
```

[Flask-Migrate Official Docs](https://flask-migrate.readthedocs.io/en/latest/)

---

## 10. Future Work
- **Planned Features**: List any features or improvements planned for the future.
- **Known Issues**: Document any known bugs or limitations.

---

## 11. Contributing
- **How to Contribute**: Provide guidelines for contributors (e.g., how to set up the project, coding standards, etc.).
- **Code of Conduct**: Link to or include a code of conduct for the project.

---

## 12. References
- **Links**: Include links to relevant documentation, tutorials, or resources.
- **Inspiration**: Mention any projects or designs that inspired your work.

---
