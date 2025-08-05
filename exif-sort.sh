#!/bin/bash
# Simple wrapper script for EXIF PySort

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/exif_pysort_improved.py"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: $PYTHON_SCRIPT not found"
    exit 1
fi

# Run the Python script with all arguments passed through
python3 "$PYTHON_SCRIPT" "$@"
