#!/usr/bin/env python
import thread
from socket import *
import sys
import time
from threading import Thread
import datetime

# Inclui a bilbioteca pyGalileo no PYTHON PATH
# para leitura das I/Os
galileo_path = "/var/project"
if galileo_path not in sys.path:
    sys.path.append(galileo_path);

from pyGalileo import *

# Define as constantes do server
ADDR = ''
PORT = 80
N_CONN = 50
BUFFER = 512
PAGE_NAME = "index.html"
TEMP_PIN = A0
LUM_PIN = A1
REFRESH_PERIOD = 5

def generateResponse(isValidRequest):
    # Caso a requisicao nao seja valida, retorne erro 400 Bad Request
    if (not isValidRequest):
        response = ("HTTP/1.1 400 Bad Request\n"
            "Content-type: text/plain\n"
            "Content-length: 22\n\n"
            "Error 400. Bad Request")
        return response
    # Requisicao valida, prossiga

    # Le o arquivo html especificado em PAGE_NAME
    page = open(PAGE_NAME, "r")
    # pageStr armazena em string todo o arquivo
    pageStr = page.read()
    page.close()

    # Gera o header desta requisicao
    header = ("HTTP/1.1 200 OK\n"
        "Content-Type: text/html; charset=UTF-8\n"
        "Content-Encoding: UTF-8\n"
        "Content-Length: %d\n"
        "Server: SimpleServer\n"
        "Connection: close\n\n"
        ) % len(pageStr)

    # Concatena o header e o arquivo html para gerar a resposta
    response = "%s%s" % (header, pageStr)
    return response

# Valida se a requisicao HTTP e valida
def validateHTTPRequest(request):
    # Separa a requisicao em items por whitespace
    listRequest = request.split()
    # Se a lista tiver menos de dois itens, a requisicao e invalida
    if (len(listRequest) < 2):
        return False
    # Se o primeiro parametro nao for um GET, a requisicao e invalida
    if (listRequest[0] != "GET"):
        return False
    # Se o segundo parametro nao requisitar o padrao, a requisicao e invalida
    if (listRequest[1] != "/" and listRequest[1] != "/index.html"):
        return False
    # Se passar estas condicoes, a requisicao e valida
    return True

# Trata das requisicoes TCP em uma thread separada
def handler(client_socket, addr):
    # Recebe dados (provavelmente HTTP)
    dataRecv = client_socket.recv(BUFFER)
    # Envia a resposta gerada pela funcao generateResponse()...
    # de volta para o client
    client_socket.sendall(generateResponse(validateHTTPRequest(dataRecv)))
    # Fecha a conexao
    client_socket.close()
    # Termina a thread
    return

# Thread que atualizara o conteudo de index.html com os valores mais atuais dos sensores
class UpdateSensorValues(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.kill_received = False
        self.counter = 0

    def run(self):
        while (not self.kill_received):
            # Le a temperatura e a luminosidade pelos pinos analogicos do Galileo
            # Aqui e onde a biblioteca pyGalileo e utilizada
            temperature = analogRead(TEMP_PIN)
            luminosity = analogRead(LUM_PIN)
            # Le o arquivo padrao, onde as strings $hora, $temp e $lum serao
            # substituidas pelos valores corretos
            file = open('index_std.html', 'r')
            fileStr = file.read()
            file.close()

            # Adquiri o tempo do sistema
            n = datetime.datetime.now()
            # Formata a hora
            timeStr = "%02d:%02d:%02d %d/%d/%d" % (n.hour, n.minute, n.second, n.day, n.month, n.year)

            # Substitui as strings em index_std.html para gravar em index.html
            fileStr = fileStr.replace("$hora", timeStr)
            fileStr = fileStr.replace("$temp", str(temperature))
            fileStr = fileStr.replace("$lum", str(luminosity))
            fileStr = fileStr.replace("$counter", str(self.counter))

            # Escreve as mudancas em index.html
            fileWrite = open("index.html", "w+")
            fileWrite.write(fileStr)
            fileWrite.close()

            # Incrementa o contador de leituras
            self.counter += 1
            # Dorme por N segundos, define o tempo de atualizacao da leitura
            # dos sensores
            time.sleep(REFRESH_PERIOD)

# Ponto de entrada do codigo
if __name__ == "__main__":
    # Cria a thread para atualizar os valores dos sensores
    threadSensor = UpdateSensorValues()
    threadSensor.start()

    # Cria um socket IPv4/TCP
    sock = socket(AF_INET, SOCK_STREAM)
    # Possibilita reutilizacao da porta caso reiniciado
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    # Vincula socket ao endereco e porta especificados
    sock.bind((ADDR, PORT))
    # Escuta por N conexoes
    sock.listen(N_CONN)
    print "Listening on port", PORT
    try:
        # Loop infinito aceitando conexoes pendentes
        while True:
            # Aceita conexao e adquiri informacoes sobre o cliente
            client_socket, client_addr = sock.accept()
            # Print endereco IP da nova conexao
            print 'Connection from',  client_addr
            # Cria nova thread para tratar da requisicao
            thread.start_new_thread(handler, (client_socket, client_addr))
    # Sinaliza thread de leitura do sensor para ser terminada
    except:
        threadSensor.kill_received = True
    # Fecha o socket. Usada dentro do bloco finally para garantir a execucao
    finally:
        sock.close()
    print "Server was killed"

