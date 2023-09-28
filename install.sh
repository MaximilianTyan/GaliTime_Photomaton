#!/bin/bash

# Installation script for the various packages
# of Galitime Photomaton

# ----------------------------------
# Using nala installer allows to have an
# undo-able package install history

read -r -p "Install using nala (undo-able apt) ? [y/n]"
if [[ $REPLY = "y" ]]
then
    echo "Installing nala ..."
    sudo apt install nala

    echo "Creating temporary alias for nala ..."
    alias apt="nala"
fi

# -----------------------------------
echo "Installing linux packages ..."
sudo apt install -y python3 python3-pip python3-venv 
sudo apt install -y printer-driver-gutenprint
sudo apt install -y gphoto2 libgphoto2-dev
sudo apt install -y python3-pyqt5

# -----------------------------------
echo "Creating env folder using venv ..."
python3 -m venv env --prompt galitime
source env/bin/activate

# -----------------------------------
echo "Installing python packages ..."
python3 pip install gphoto2
python3 pip install pyqt5 
python3 pip install pycups

deactivate

# -----------------------------------
echo "Removing nala alias ..."
alias -r nala

echo "Install done"
