#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"


APP_PATH="$SCRIPT_DIR/launcher.py"

PID=$(pgrep -f "$APP_PATH")

if [ -n "$PID" ]; then
    echo "Launcher is already running (PID $PID). Closing it..."
    kill $PID
    exit 0
else
    echo "Starting launcher..."
    python3 "$APP_PATH" &
    exit 0
fi
