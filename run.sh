#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "🏈 Launching Jayme's ESPN Fantasy Draft Engine"
echo "=========================================================="

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
    echo "Installing requirements..."
    uv pip install streamlit pandas numpy pyyaml
fi

echo "Starting Streamlit Draft Command Center..."
echo "Opening browser at http://localhost:8501 ..."

.venv/bin/streamlit run app.py --server.port 8501 --server.headless false
