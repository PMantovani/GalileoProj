#!/bin/sh

# Arruma o fuso horário
export TZ=America/Sao_Paulo
# Mata o servidor http padrão embarcado
killall lighttpd
# Sobe com o endereço IP fixo
ifconfig enp0s20f6 192.168.25.32 netmask 255.255.255.0 up
# Roda o servidor web e o cliente de log
cd /var/project/
nice -n -11 python logclient.py &
nice -n -1  python simple_server.py &
#não sei se vai funcionar, mas teoricamente isso vai iniciar o processo setando essas prioridades.
