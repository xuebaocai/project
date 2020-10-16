#!/bin/bash

sudo apt-get install libssl-dev
sudo apt-get install libcurl4-gnutls-dev
sudo apt-get install libghc-gnutls-dev
sudo apt-get install unattended-upgrades
sudo apt-get install python3-pip python3-dev
python3 -m pip install --upgrade pip==20.0.2

sudo pip3 install chardet enum34 future numpy pycurl pygobject python-apt
sudo pip3 install requests setuptools six ssh-import-id  urllib3 wheel
sudo pip3 install Paho-mqtt Protobuf Imutils
sudo pip3 install setuptools==20.7.0

