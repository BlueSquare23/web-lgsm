# Web-LGSM Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.8.7 - unreleased]

### Added

- Created new `ControlService` class as service for interacting with controls data.
- Created new `ConfigManager` class for handling main.conf ConfigParser stuff.

### Changed

- Renamed "Command" to "Controls" through projects source (where applicable).

### Fixed

- Upgrade pip requirement `requests` to v2.32.5 (thanks dependabot!).

## [v1.8.6 - 2025-11-22]

### Added

- Add basic anti-brute force lockout protection to login page.
- Add ability to toggle password visibility to all password forms.
- Add ability to reset TOTP 2fa secret via web-lgsm.py script.
- Add TOTP Two Factor Auth option for web panel login!
- Add Password Strength indicator to password setup fields.

### Changed

- Change style for Edit User page, integrate password strength indicator.
- Change style for Setup page, integrate password strength indicator.

### Fixed

- Fix delete server with jobs to cleanup jobs first.
- Fix alert messages to push down rest of page.

## [v1.8.5 - 2025-08-17]

### Added

- Add ability to edit GameServer info via existing `/add` page / route.
- Add new audit log file and interface for searching recent log entries.
- Add jinja2 extension for loop controls to enable `continue` & `break` in templates.
- Add caching for authed ssh client objects to cut down ssh response times.
- Add new cronjob manager interface for manipulating system's crontab.

### Changed

- Change install page layout and add pictures for game servers!
- Remove unique constraint on GameServer names.
- Upgrade project to use Bootstrap 5.3.7.

### Fixed

- Fix web-lgsm docker start race condition [Issue #44](https://github.com/bluesquare23/web-lgsm/issues/44)
- Fix headless auto updates by coming up with new update mechanism.
- Fix alert bootstrap / html to make backend alerts dismissible.

## [v1.8.4] - 2025-06-15

### Added

- Add Flask-Cache caching for cfg buttons on controls page.
- Add fully fleshed-out [DESIGN.md](https://github.com/BlueSquare23/web-lgsm/blob/master/docs/DESIGN.md) doc.
- Add Flask-Migrate (Alembic) for handling database migrations between versions.
- Add code coverage report as CI/CD artifact for later perusing.
- Add documentation about test code.

### Changed

- Improved testing infrastructure to level ground for continued growth.
- Change auth cookies from `SameSite: None` to `SameSite: Lax` for sec reasons.
- Change edit page to accept `cfg_path` & `server_id` via GET args.
- Change form handling to use Flask-WTF & WTForms for validation.
- Restructure test code to ensure _independence_ and _idempotency_.

### Fixed

- Fix `install.sh --docker` for Debian. [Github Issue](https://github.com/BlueSquare23/web-lgsm/issues/41)
- Fix CSRF vulnerabilities in applications forms with Flask-WTF & WTForms.
- Fix core update mechanism in `web-lgsm.py`, with Alembic for database upgrades.
- Fix test code to ensure every test can be run in isolation and its pass/fail
  status will not affect any other tests.

---

## [v1.8.3] - 2025-04-11

### Added

- Add builtin swagger documentation for project's API.
- Make new /api/delete API route for removing game servers.
- Create `api.py` file for holding API routes.
- Add `processes_global.py` as module level singleton for holding process objects.
  - List of `proc_info` objects. Global singleton shared between Views, Utils, & API.
- Add `uninstall.sh` script for removing system level components of web app.

### Changed

- Make individual & multi GameServer delete buttons work via new API route.
- Make API endpoints utilize real `flask_restful` module for building out API.
- Transition codebase to use game server ID instead of name as main identifier.
- Make GameServers use UUIDs now for primary key.
- Make `install.sh` install playbooks, venv, and `ansible_connector.py` as root
  in system level directories for security reasons.

### Fixed

- Fix install output being displayed on Controls page immediately following
  GameServer install. Now output is cleared post install.
- Fix tests to work with newest changes.
- Fix cached null socket file name after fresh install bug. 
  - Now on game server start, will purge cache entry if socket file name is null.

---

## [v1.8.2] - 2025-03-30

### Added

- Add `main.conf.local` override file. For if users would like to keep a local
  copy of the `main.conf` file that will be ignored by updates.
- Add `main.conf` options for `cert` and `key` to enable SSL for Gunicorn server.
- Add new changelog html page / route that reads from local copy of this file.
- Add iframe include for changelog on about page.

### Changed

- Remove now deprecated temp sudoers rule add for non-same user game server
  install playbook.
- Change docker deployment to work via single user mode.
- Change supported versions in `SECURITY.md`, deprecate v1.7.x.
- Mark `web-lgsm.py --update` flag as broken atm. Will fix soon.

### Fixed

- Fix install same/single user mode to install required apt requirements.

---

## [v1.8.1] - 2025-03-22

### Added

- New `docs/DESIGN.md` design document file to help others understand how the
  app is built.

### Added

- New `CHANGELOG.md` file for keeping track of changes.

### Fixed

- Fix bug for local install same user status indicators.

---

