#!/bin/sh

# Define o fuso horario
export TZ=America/Sao_Paulo
# Mata o servidor http padrao embarcado
killall lighttpd
# Sobe com o endereco IP fixo
ifconfig enp0s20f6 192.168.25.32 netmask 255.255.255.0 up
# Roda o servidor web e o cliente de log
cd /var/project/
# Define as prioridades bases iniciais dos processos
nice -n -11 python logclient.py &
nice -n -1  python simple_server.py &
