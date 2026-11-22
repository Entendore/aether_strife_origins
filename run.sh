#!/bin/bash
# Run Aether Strife: Origins

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the game
python src/game.py
