#!/bin/bash
# Fantasy RPG Game Launcher (Unix/Linux/macOS)

echo "🗡️  Starting Fantasy RPG..."
echo

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Run the game
python3 play.py