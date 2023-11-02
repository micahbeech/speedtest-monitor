#!/bin/sh

set -e

requiredPythonVersion="3.11"
if ! python versioncheck.py $requiredPythonVersion; then
  echo "Error! You are running $(python -V)"
  echo "Please ensure your Python version is at least $requiredPythonVersion"
  exit 1
fi

echo "Installing python dependencies..."
pip install -q -r requirements.txt
echo "Done."
echo

python setup.py 
