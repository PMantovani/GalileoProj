#!/bin/sh

killall lighttpd
ifconfig enp0s20f6 192.168.25.32 netmask 255.255.255.0 up
cd /var/project/
nice -n -11 python logclient.py &
nice -n -1  python simple_server.py &
#não sei se vai funcionar, mas teoricamente isso vai iniciar o processo setando essas prioridades.