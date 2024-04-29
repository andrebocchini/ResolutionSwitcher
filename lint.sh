#!/usr/bin/env sh

pyright src/*.py

if [[ $? -ne 0 ]]; then
    echo
    echo -n "Pyright detected errors that need to be fixed. Exiting."
    exit 1
fi
ruff check --select I --fix --config ruff.toml
ruff format --config ruff.toml
