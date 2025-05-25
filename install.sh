#!/usr/bin/env bash
set -e

# UaiBot install script (cross-platform, agentic)
# Usage:
#   ./install.sh [dev|test|all]
#   (no argument = core install)

echo "[UaiBot] Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "[UaiBot] Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

EXTRA=""
if [ "$1" == "dev" ]; then
  EXTRA="[dev]"
elif [ "$1" == "test" ]; then
  EXTRA="[test]"
elif [ "$1" == "all" ]; then
  EXTRA="[all]"
fi

echo "[UaiBot] Installing dependencies: pip install .${EXTRA}"
pip install .${EXTRA}

PYVER=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')
if [[ "$PYVER" < "3.12" ]]; then
  echo "[WARNING] Python 3.12+ is recommended for full compatibility."
fi

PLATFORM=$(uname -s)
echo "[UaiBot] Detected platform: $PLATFORM"

if [[ "$PLATFORM" == "Linux" ]]; then
  echo "[UaiBot] For audio features, you may need: sudo apt-get install portaudio19-dev"
fi

echo "[UaiBot] Install complete. To activate your venv:"
echo "  source .venv/bin/activate"
echo "To run CLI:"
echo "  PYTHONPATH=src python3 scripts/launch.py"
echo "To run GUI:"
echo "  PYTHONPATH=src python3 scripts/launch_gui.py" 