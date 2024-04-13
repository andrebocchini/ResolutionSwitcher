#/bin/sh

pylint --errors-only src/*.py

if [[ $? -ne 0 ]]; then
    echo
    echo -n "Pylint detected errors that need to be fixed. Exiting."
    exit 1
fi

ruff format
