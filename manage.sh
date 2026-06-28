#!/usr/bin/env bash

# SentinelX Management Script

set -e

# Base directory of the script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$DIR/venv/bin/python"
VENV_PYTEST="$DIR/venv/bin/pytest"

function print_help() {
    echo "SentinelX Management Helper Script"
    echo "Usage: ./manage.sh [command]"
    echo ""
    echo "Commands:"
    echo "  run        - Run SentinelX with default configurations"
    echo "  test       - Run all unit and integration tests"
    echo "  mock-logs  - Run the mock log generator to simulate traffic"
    echo "  lint       - Run syntax verification on code files"
    echo "  clean      - Clean up temporary files, state, and caches"
    echo "  help       - Print this help message"
}

case "$1" in
    run)
        "$VENV_PYTHON" "$DIR/run.py" "${@:2}"
        ;;
    test)
        PYTHONPATH="$DIR" "$VENV_PYTEST" "${@:2}"
        ;;
    mock-logs)
        "$VENV_PYTHON" "$DIR/generate_mock_logs.py" "${@:2}"
        ;;
    lint)
        "$VENV_PYTHON" -m py_compile "$DIR/run.py" "$DIR/config.py" "$DIR/core/"*.py "$DIR/tests/"*.py
        echo "Syntax verification passed."
        ;;
    clean)
        rm -rf "$DIR/.pytest_cache"
        rm -rf "$DIR/__pycache__" "$DIR/core/__pycache__" "$DIR/tests/__pycache__"
        rm -f "$DIR/sentinelx_state.json" "$DIR/sentinelx_state.json.tmp"
        rm -f "$DIR/mock_auth.log"
        echo "Clean completed."
        ;;
    help|*)
        print_help
        ;;
esac
