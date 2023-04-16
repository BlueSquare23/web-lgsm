#!/usr/bin/env bash
# Wraps pytest to setup testing env.

if [[ -z "$VIRTUAL_ENV" ]]; then
    source venv/bin/activate
fi

rm app/database.db

python -m pytest
