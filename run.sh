#!/bin/bash
# Argus Overview v2.3 Launcher
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Use venv python directly if available, otherwise system python
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

if [ -f "venv/bin/python3" ]; then
    exec venv/bin/python3 src/main.py "$@"
elif [ -f ".venv/bin/python3" ]; then
    exec .venv/bin/python3 src/main.py "$@"
else
    exec python3 src/main.py "$@"
fi
