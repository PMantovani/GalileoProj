#!/usr/bin/env python
import thread
from socket import *
import sys
import time
from threading import Thread
import datetime
import os

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

def generateResponse(validation):
    # Extrai o codigo desta requisicao e o arquivo, caso aplicavel
    code, filename = validation
    # Verifica erro 400 Bad Request
    if (code == "400"):
        response = ("HTTP/1.1 400 Bad Request\n"
            "Content-type: text/plain\n"
            "Content-length: 22\n\n"
            "Error 400. Bad Request")
        return response

    # Verifica erro 404 File not found
    if (code == "404"):
        response = ("HTTP/1.1 400 File not found\n"
            "Content-type: text/plain\n"
            "Content-length: 25\n\n"
            "Error 404. File not found")
        return response

    # Requisicao valida, prossiga

    # Caso requisicao tenha sido "/", use o arquivo especificado por PAGE_NAME
    if (filename == ""):
        filename = PAGE_NAME

    # Especifica o Content-Type para o header do HTTP
    if (filename.lower().endswith(".html")):
        cont_type = "text/html; charset=UTF-8"
    elif (filename.lower().endswith(".png")):
        cont_type = "image/png"
    elif (filename.lower().endswith(".jpg")):
        cont_type = "image/jpeg"
    elif (filename.lower().endswith(".ico")):
        cont_type = "image/x-icon"
    else:
        cont_type = "text/plain"

    # Le o arquivo solicitado, em formato binario caso imagem
    if (cont_type.startswith("image")):
        page = open(filename, "rb")
    else:
        page = open(filename, "r")
    # pageStr armazena em string todo o arquivo
    pageStr = page.read()
    page.close()

    # Gera o header desta requisicao
    header = ("HTTP/1.1 200 OK\n"
        "Content-Type: %s\n"
        "Content-Encoding: UTF-8\n"
        "Content-Length: %d\n"
        "Server: SimpleServer\n"
        "Connection: close\n\n"
        ) % (cont_type, len(pageStr))

    # Concatena o header e o arquivo html para gerar a resposta
    response = "%s%s" % (header, pageStr)
    return response

# Valida se a requisicao HTTP e valida
def validateHTTPRequest(request):
    # Separa a requisicao em items por whitespace
    listRequest = request.split()
    # Se a lista tiver menos de dois itens, a requisicao e invalida
    if (len(listRequest) < 2):
        return ("400", "")
    # Se o primeiro parametro nao for um GET, a requisicao e invalida
    if (listRequest[0] != "GET"):
        return ("400", "")
    # Caso o segundo parametro nao comece com /
    if (not listRequest[1].startswith("/")):
        return ("400", "")
    # Corta o / da frente da requisicao
    stripRequest = listRequest[1][1:]
    # Evita que a requisicao acesse niveis superiores do sistema
    if (".." in stripRequest):
        return ("400", "")
    # Verifica se o arquivo existe no sistema, e se requisicao nao foi /
    if (not os.path.isfile(stripRequest) and stripRequest != ""):
        return ("404", "")
    # Se passar estas condicoes, a requisicao e valida
    return ("200", stripRequest)

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

