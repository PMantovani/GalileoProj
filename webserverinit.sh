#!/bin/sh

killall lighttpd
ifconfig enp0s20f6 192.168.25.32 netmask 255.255.255.0 up
cd /var/project/
python logclient.py &
python simple_server.py &
