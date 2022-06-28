#!/bin/bash
# 
# Bugfix: execute once the following line:
# echo 'export CHROMIUM_FLAGS="$CHROMIUM_FLAGS --use-gl=egl"' | sudo tee /etc/chromium.d/egl
# https://forums.raspberrypi.com/viewtopic.php?p=1990610#p1990146
#
# Starting the webserver and webbrowser at startup configured according to:
# https://pimylifeup.com/raspberry-pi-kiosk/
#

xset s noblank
xset s off
xset -dpms
unclutter -idle 2 -root &

sudo -u pi bash
echo Starting magisterka project
/usr/bin/python3 /home/pi/magisterka/app.py &
sleep 3
/usr/bin/chromium-browser --app=http://localhost:8080/dashboard --kiosk

