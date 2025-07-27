#!/usr/bin/env bash

echo "--- Setting up Python virtual environment ---"

if [ ! -d ".venv" ]; then
  echo "Creating new virtual environment at ./.venv"
  python -m venv .venv
else
  echo "Virtual environment already exists at ./.venv"
fi

source .venv/bin/activate
echo "Virtual environment activated."

if [ -f "requirements.txt" ]; then
  if [ "$(ls -A .venv/lib/python*/site-packages/ 2>/dev/null)" = "" ]; then
    echo "Installing Python dependencies from requirements.txt..."
    pip install -r requirements.txt
    echo "Dependencies installed."
  else
    echo "Dependencies already installed. Skipping pip install."
  fi
else
  echo "requirements.txt not found. Skipping pip install."
fi

echo "--- Environment setup complete ---"
