# Web-LGSM Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- Add `main.conf.local` override file. For if users would like to keep a local
  copy of the `main.conf` file that will be ignored by updates.
- Add `main.conf` options for `cert` and `key` to enable SSL for Gunicorn server.
- Add new changelog html page / route that reads from local copy of this file.
- Add iframe include for changelog on about page.

### Changed

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

