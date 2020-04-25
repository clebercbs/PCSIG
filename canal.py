#!/usr/bin/python
# coding: utf-8

#Envio de mensagens

import socket
import time
import json
import numpy as np
import sys
import random

timestamp = time.time()
colisoes = []
conjunto_colisoes = set()

backoff = 0
latencia = 0.0
host = '255.255.255.255'
port = 44444

lider_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
lider_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
lider_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lider_socket.bind((host, port))

def enviarMensagem(mensagem, total_pelotoes, valor):
    global latencia
    global backoff
    global timestamp
    global lider
    latencia = float(total_pelotoes)*0.02701
    backoff = random.uniform(0.001,0.030)
    time.sleep(latencia+backoff) #período de back-off aleatório
    
    ###################### Simulando perda de mensagens #####################
    resultado = np.arange (start = 1, stop = 3)
    perdaDeMensagens = np.random.choice (a = resultado, p = [1-valor, valor])
    if perdaDeMensagens == 1:
        message = json.dumps(mensagem)
        lider_socket.sendto(message.encode(), (host, port))
    else:
        message = json.dumps("lost")
        lider_socket.sendto(message.encode(), (host, port))

    ######################  Contabilizando as colisões #####################
    
    if message:
        with open('colisoes.txt', 'a') as arq:
            arq.write(str('{0:.6f}'.format(time.time())))
            arq.write(',')
    
    ##########################################################


















