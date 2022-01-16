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
2) enable i2c interface
3) enable 1-wire interface (gpio4)
4) sudo reboot 
5) sudo i2cdetect -y 1 - to check whether i2c interface has been enabled properly

#HMC
0) used pins: MOSI-GPIO10, MISO-GPIO9, CLK-GPIO11, CS-GPIO8,  remember to set P/S pin to high to enable serial mode interface
1) sudo raspi-config
2) enable SPI interface
3) Either reboot your Pi or run this command: sudo modprobe "spi-bcm2708" to load the kernel module
4) ls -l /dev/spidev* - to check if you see two spi device

