#!/usr/bin/env sh

uv run --extra lint pyright

if [[ $? -ne 0 ]]; then
    echo
    echo -n "Pyright detected errors that need to be fixed. Exiting."
    exit 1
fi
uv run --extra lint ruff check --select I --fix
uv run --extra lint ruff format
