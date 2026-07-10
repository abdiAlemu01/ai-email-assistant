#!/usr/bin/env bash
# Install backend dependencies using uv
cd "$(dirname "$0")"
uv add -r requirements.txt
uv pip list

echo "To run scripts using the same environment, use: uv python <script>.py"
