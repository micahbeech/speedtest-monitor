#!/bin/sh

echo "Installing python dependencies..."
pip install -q -r requirements.txt
echo "Done."
echo

python setup.py 
