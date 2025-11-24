# Object Oriented Design Doc

## Overview

This application has thus far Not been build with any real Object Oriented
Design in mind. But we're changing that now and that's why this document
exists.

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

### Main Problems

* [ ] **The utils.py file is bloated, unorganized, and untestable!**
  - Needs broken up into a bunch of different classes!

* [ ] **Apps module code needs to be re-organized**
  - Take for example the `forms.py` file. Too many classes all in one file.
  - I might want to break that up into a directory of class files instead.
  - But in general, that code shouldn't be sprinkled with the main route, api,
    and models scripts. Needs to be seperated out carefully into its own dirs.

* [ ] **Module code needs separated and decoupled from app scripts**
  - Things are too tightly linked and interfaces need made standard and generic.
  - Need to embrace polymorphism.


### New Preposed Structure

We're going to package up functionality and move classes into their own
directories. This alone is probably going to take a while.

```
web-lgsm/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── post.py
│   ├── forms/                   # WTForms classes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── post.py
│   ├── routes/                  # View functions
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── main.py
│   │   └── api.py
│   ├── templates/               # Jinja2 templates
│   ├── static/                  # CSS, JS, images
│   └── utils/                   # Helper classes/functions
│       ├── __init__.py
│       └── helpers.py
├── tests/                       # Test suite
├── requirements.txt
└── web-lgsm.py                  # Entry point
```


