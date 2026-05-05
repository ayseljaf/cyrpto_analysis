#!/bin/bash
# Activate virtual environment script

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

echo "✅ Virtual environment activated!"
echo "Python: $(which python)"
echo "Pip: $(which pip)"
echo ""
echo "To deactivate, run: deactivate"
echo ""
echo "⚠️  Note: Some Airflow dependencies (google-re2) may require system libraries."
echo "If you encounter installation errors, try:"
echo "  brew install re2  # Install RE2 library on macOS"
echo "  pip install --upgrade pip"
echo "  pip install -r requirements.txt"
