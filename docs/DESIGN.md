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
- **Testing Strategy**: Describe the testing approach (e.g., unit tests, integration tests).
- **Test Coverage**: Mention any tools used for test coverage (e.g., pytest, coverage.py).

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
