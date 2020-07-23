#!/bin/sh

#cd ~
#cd Documents/tobalobs/
#python monitor.py 999 &
#cd ~

sudo python3 sketchbook/tobalobs/rpi-ws.py &
python sketchbook/tobalobs/ngrok.py &
