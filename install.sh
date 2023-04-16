#!/bin/bash

echo creating Python virtual environment...
python -m venv env

source ./env/bin/activate

pip3 install -r requirements.txt

