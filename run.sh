#!/bin/bash
# EVE Veles Eyes v2.2 Launcher
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Use venv python directly if available, otherwise system python
if [ -f "venv/bin/python3" ]; then
    exec venv/bin/python3 src/main.py "$@"
elif [ -f ".venv/bin/python3" ]; then
    exec .venv/bin/python3 src/main.py "$@"
else
    exec python3 src/main.py "$@"
fi
