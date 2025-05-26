#!/bin/bash
set -e

# Labeeb install script (cross-platform, agentic)
# Usage:
#   ./install.sh [dev|test|all]
#   (no argument = core install)

echo "[Labeeb] Creating virtual environment..."
python -m venv venv
source venv/bin/activate

echo "[Labeeb] Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

EXTRA=""
if [ "$1" == "dev" ]; then
  EXTRA="[dev]"
elif [ "$1" == "test" ]; then
  EXTRA="[test]"
elif [ "$1" == "all" ]; then
  EXTRA="[all]"
fi

echo "[Labeeb] Installing dependencies: pip install .${EXTRA}"
pip install .${EXTRA}

PYVER=$(python -c 'import sys; print("%d.%d" % sys.version_info[:2])')
if [[ "$PYVER" < "3.12" ]]; then
  echo "[WARNING] Python 3.12+ is recommended for full compatibility."
fi

PLATFORM=$(uname)
echo "[Labeeb] Detected platform: $PLATFORM"

if [ "$PLATFORM" = "Linux" ]; then
    echo "[Labeeb] For audio features, you may need: sudo apt-get install portaudio19-dev"
fi

echo "[Labeeb] Install complete. To activate your venv:"
echo "source venv/bin/activate"
echo "To run CLI:"
echo "  PYTHONPATH=src python3 scripts/launch.py"
echo "To run GUI:"
echo "  PYTHONPATH=src python3 scripts/launch_gui.py" 