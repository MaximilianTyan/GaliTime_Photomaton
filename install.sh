#!/bin/bash

sudo apt install python3 python3-pip python3-venv
sudo apt install gutenprint
sudo apt install gphoto2 libgphoto2-dev
sudo apt install python3-pyqt5

python3 -m venv env --prompt galitime
source env/bin/activate

python3 pip install gphoto2 pyqt5

deactivate

echo "Install done"
