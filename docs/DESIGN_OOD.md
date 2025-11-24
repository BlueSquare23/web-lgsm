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


