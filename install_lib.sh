#!/bin/sh

# INSTALL PACKAGES
sudo apt-get update -y
sudo apt install git
sudo apt install python3 idle3
sudo apt-get install python3-pip

#download repo 
sudo git clone https://github.com/addussk/magisterka.git
sudo python3 -m pip install dash
sudo python3 -m pip install dash_daq
sudo python3 -m pip install dash-extensions
sudo python3 -m pip install Flask
sudo python3 -m pip install Flask-SQLAlchemy
sudo python3 -m pip install w1thermsensor
sudo pip3 install adafruit-circuitpython-ads1x15
sudo python3 -m pip install pyserial

#configure ADC
1) sudo raspi-config
2) enable i2c intarface
3) sudo i2cdetect -y 1 - to check whether i2c interface has been enabled properly
