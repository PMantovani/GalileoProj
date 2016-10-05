#!/bin/sh

killall lighttpd
ifconfig enp0s20f6 down
ifconfig enp0s20f6 192.168.25.32 netmask 255.255.255.0 up
cd /var/project/
python server1.py
