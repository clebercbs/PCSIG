#!/usr/bin/python
# coding: utf-8
import socket
import time
import json
import threading
import numpy as np
import sys
import random
from canal import enviarMensagem

idLider = str(sys.argv[1])              #Define idLider
valor = float(sys.argv[2])              #Simulação de perda de mensagens
total_pelotoes = float(sys.argv[3])     #Quantidade de pelotões que deseja simular 
tempoLimite = int(sys.argv[4])          #Valor do tempoLimite (1000; 2000; 3000; 4000; 5000 ms)
lista_mensagens = []
conjunto_colisoes = set()

v_id = idLider                              #é considerado que o id do líder endereça a visão
idVisao = 0                                 #o valor dessa variável é alterada sempre que há uma mudança de visão (no pseudocódigo, o idVisao e o v_id estão juntas
contexto = 'Platoon'                        #representa o contexto ou aplicação do grupo de veículos
periodo = 0                                 #variável utilizada para a contagem de tempo
atualizaVisao = 0                           #variável utilizada para auxiliar na simulação da atualização da visão
visao = ()                                  #tupla que recebe (v_id, idVisao, membros, contexto)
membros = ['l_1',  'f_1']                   #lista contendo os veículos que fazem parte do grupo. l_s líder e f1_s seguidor do grupo s
visoesSincronizadas = []                    #recebe as visões sincronizadas na TAREFA T3
mensagensRecebidas = []                     #recebe as mensagens na TAREFA T2
mensagensTemporarias = []                   #variável temporária utilizada na TAREFA T2
visoesTemporarias = []                      #variável temporária utilizada na TERAFE T3
visoesConhecidas = []
cronometro = 0                              #variável utilizada para a contagem de tempo
sinc = 0
i1 = 0
i2 = 0
cont_envia = 0
qtd = 0
envios = 0
sem = threading.Semaphore()

host = '255.255.255.255'
port = 44444

lider_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
lider_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
lider_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lider_socket.bind((host, port))

#TAREFA T1: envio periódico de mensagens

def enviar():
    global mensagensRecebidas
    global idLider
    global idVisao, sem
    global atualizaVisao
    global visao
    global membros
    global visoesConhecidas
    global valor
    lideres = []
    v_aux = []
    #linha 9 - para cada m em mensagensRecebidas faça:
    for m in mensagensRecebidas:
        #linha 10 - para cada v em visoesConhecidas fala:
        for v in visoesConhecidas:
            if v is None:
                print 'Visoes Conhecidas vazias'
                #linha 11 - se v.lider = m.idLider então:
                if m[0][0] == v[0][0]:
                    #linha 12 - visoesConhecidas <- visoesConhecidas \ {v}
                    visoesConhecidas.remove(v)
                else:
                    print 'nok'
        #linha 15
        if m[0][0] != idLider:
            if m[0][0] not in lideres:
                lideres.append(m[0][0])
    for lider in lideres:
        for m in mensagensRecebidas:
            if m[0][0]==lider:
                v_aux = m[1][0:2]
        if v_aux not in visoesConhecidas:
            #linha 16 visoesConhecidas <- visoesConhecidas U {m.visao}
            visoesConhecidas.append(v_aux)
    sem.acquire()
    visao = v_id, idVisao, membros, contexto
    #linha 19 mensagem <- (idLider,visao,visoesConhecidas)
    mensagem = idLider, list(visao), visoesConhecidas 
    sem.release()
    #linha 20 enviarMensagem(mensagem)
    enviarMensagem(mensagem, total_pelotoes, valor)
    
def manutencao(*args):
    global mensagensTemporarias, sem
    global visoesSincronizadas
    global visoesTemporarias
    global visao
    global idLider
    global total_pelotoes
    global tempoLimite
    global cronometro
    global qtd
    mensagensTemporarias = list(args)
    lideres = []
    vid2 = []
    mensagensTemporarias_aux = []
    #linha 31 - para cada m em mensagensTemporarias:
    for m in mensagensTemporarias:
        #linha 32 - se m.idLider != idLider:
        if m[0][0] != idLider:
            if m[0][0] not in lideres:
                lideres.append(m[0][0])
    for lider in lideres:
        for m in mensagensTemporarias:
            if m[0][0] == lider:
                vid_aux = m
        mensagensTemporarias_aux.append(vid_aux)
    #Segui a ideia do pseudocódigo, analisando as informações contidas nas visões conhecidas. Busquei as informações do v_id utilizando
    #recursos de consulta à lista, por isso que não está sendo demonstrado visõesConhecidas na TAREFA T2 manutenção.
    #linha 33 - para cada v em em visoesConhecidas faça:
    for vid in mensagensTemporarias_aux:
        vis = list(visao)
        v =  vis[0:2]
        res = [str(v_id) for v_id in vid[2]]
        for l2 in res:
            vid2 = (l2[2:-1])
            #linha 34 - v = visao
            if str(v)[1:-1] == vid2:
                with open('visaoSincronizada.txt', 'a') as arq_vis:
                    arq_vis.write(str(cronometro))
                    arq_vis.write(str(idLider))
                    arq_vis.write(vid[0])
                    arq_vis.write('\n')
                #linha 35 - visoesTemporarias <- visoesTemporarias U {v}
                visoesTemporarias.append(vid[0:-1])     
    #linha 40 - visoesSincronizadas <- visoesTemporarias
    visoesSincronizadas = visoesTemporarias
    print 'Visoes sincronizadas do lider: ', idLider, visoesSincronizadas
    #linha 41 - visoesTemporarias <- 0
    del visoesTemporarias[:]
    #linha 42 - mensagensRecebidas <- 0
    del mensagensRecebidas[:]

#TAREFA T2: recebimento de mensagens
def receber():
    global mensagensRecebidas
    global cronometro
    global mensagensTemporarias
    global idLider
    global sem
    global tempoLimite
    global lista_mensagens
    #linha 25 - tempAux <- 0
    tempAux = 0.0
    t = tempoLimite/1000
    #linha 26 - enquanto True faça:
    while True:
        data, addr = lider_socket.recvfrom(4096)
        receberMensagem2 = json.loads(data)
        if receberMensagem2 != "lost":
            receberMensagem = receberMensagem2
        else:
            receberMensagem = [idLider, [idLider, 0, ["Platoon"], []]]
        #linha 27 - mensagensRecebidas <- mensagensRecebidas U {receberMensagem()}
        mensagensRecebidas.append(receberMensagem)
        #linha 28 - se cronometro = tempAux + tempoLimite entao
        if cronometro == tempAux + t:
            sem.acquire()
            #linha 29 - mensagensTemporarias <- mensagensRecebidas
            mensagensTemporarias = mensagensRecebidas
            #linha 30 - tempAux <- cronometro
            tempAux = cronometro
            t2_manutencao = threading.Thread(target=manutencao, args=mensagensTemporarias)
            t2_manutencao.start()
            sem.release()
        
        
        ################################## Lod de eventos ################################      
        
        with open('recebimento_envio.txt', 'a') as arq:
            arq.write(str(i1))
            arq.write(' - ')
            arq.write(' Recebidas ')
            arq.write(str(idLider))
            arq.write('\n')
            arq.write(str(i2))
            arq.write(' - ')
            arq.write(' Perdidas ')
            arq.write(str(idLider))
            arq.write('\n')

        ##################################################################################
tarefa2 = threading.Thread(target=receber)
tarefa2.start()

#linha 8 -> enquanto True faça
while True:
    periodo = 0.5
    tarefa1 = threading.Thread(target=enviar)
    tarefa1.start()
    #linha 21 - sleep(periodo)
    time.sleep(periodo)
    cronometro += 0.5
    cont_envia += 1

############################# CONTABILIZAÇÃO E VALIDAÇÃO DOS DADOS ##############################

    if cont_envia == 201:
        try:
            if tempoLimite == 1000:
                qtd = 100
                envios = 2
            elif tempoLimite == 2000:
                qtd = 50
                envios = 4
            elif tempoLimite == 3000:
                qtd = 33
                envios = 6
            elif tempoLimite == 4000:
                qtd = 25
                envios = 8
            elif tempoLimite == 5000:
                qtd = 20
                envios = 10
            else:
                print('Valor de tempo inválido')
            lista4 = []
            lista5 = []
            arq = open('/home/cleber/Defesa/visaoSincronizada.txt', 'r')
            texto = arq.readlines()
            arq.close()
            result = round(len(texto)/((total_pelotoes*(total_pelotoes-1))*qtd),4) 
            print 'Sincronizações unidirecionais com o líder ', idLider, result*100, '%'
            lista1 = [str(float(lista)) for lista in range(1,101)]
            for l0 in lista1:
                lista2 = []
                for l1 in texto:
                    if l0 == l1[-8:-3]:
                        lista2.append(l1[-3:-1])
                lista3 = [i for i in lista2 if i[::-1] in lista2]
                num = len(lista3)
                lista4.append(num)
            soma = sum(lista4)
            result2 = round(soma/((total_pelotoes*(total_pelotoes-1))*qtd),4) 
            print 'Sincronizações bidirecionais com o líder ', idLider, result2*100, '%'
           
           ############################################# Análise das colisões #############################################
            
            if valor == 0:
                arq = open('/home/cleber/Defesa/colisoes.txt', 'r')
                texto = arq.readlines()
                arq.close()
                for elemento in texto:
                    novo_conjunto = elemento.split(",")
                    for valor in novo_conjunto:
                        conjunto_colisoes.add(valor)
                resultado = int(total_pelotoes*(qtd*envios)) - (len(conjunto_colisoes)-(total_pelotoes+1))  
                print resultado, 'Colisões'
            else:
                print 'Para testar as colisões é necessário considerar uma rede sem perda de mensagens'

            ###############################################################################################################

            break
        except:
            print 'Não há visões sincronizadas!'
            break
