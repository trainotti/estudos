import json
import websocket
import time
import requests
import sqlite3
import csv


valor_compra = 0
valor_venda = 0
data_compra = 0
data_venda = 0
kvalorCompra = 0
kvalorVenda = 0
dvalorCompra = 0
dvalorVenda = 0
status = "vendido"
flagbuy = "red"
flagsell = "red"
action = ""
percentual = []
maximo_local = 0

############ Parametros externos para Simulação ############

print("******* Simulador de Trade" "*******\n")
print("Digite os parametros a serem usados\n")

data_inicio = input("Digite a data de inicio (dd-mm-aaaa): ")
hora_inicio = "00:00:00"
inicioepoch = int(time.mktime(time.strptime(data_inicio[6:10]+"-"+data_inicio[3:5]+"-"+data_inicio[0:2]+" "+hora_inicio, '%Y-%m-%d %H:%M:%S'))) - time.timezone 
data_fim = input("Digite a data de termino (dd-mm-aaaa): ")
hora_fim = "23:59:59"
terminoepoch = int(time.mktime(time.strptime(data_fim[6:10]+"-"+data_fim[3:5]+"-"+data_fim[0:2]+" "+hora_fim, '%Y-%m-%d %H:%M:%S'))) - time.timezone
limite_inferior = int(input("Digite o limite inferior da regiao do gain: "))
limite_superior = int(input("Digite o limite superior da regiao do gain: "))
start_gain = float(input("Digite o percentual para iniciar o gain - sem o simbolo %: "))/100
stop_gain = float(input("Digite o percentual do recuo que para o gain - sem o simbolo %: "))/100
stop_loss = float(input("Digite o percentual para STOP LOSS: "))/100
percentual_compra = float(input("Digite o percentual para compra: "))/100
print("\nIniciando Simulacao")
saldo = 10000
saldo_inicial = 10000
referencia_watch = 0

############################################################


with open('/home/bot01/estudo/estudos/iotusd.csv', newline ='') as csvfile:
    reader = csv.DictReader(csvfile)    
    for row in reader:
        data = int(row['data'])
        preco = float(row['preco'])
        quantidade = float(row['quantidade'])
        tipo = str(row['tipo'])
        kvalor = float(row['kvalor'])
        dvalor = float(row['dvalor'])
        fechamento = str(row['fechamento'])

        if (data >= inicioepoch and data <= terminoepoch):                        

            if (status == "vendido" and flagbuy == "red" and kvalor < 20 and dvalor < 20):
                flagbuy = "green"

            if (status == "watch" and kvalor < 20 and dvalor < 20):
                flagbuy = "green"
                status = "vendido"
                print('Data:', time.gmtime(data), 'Preco:', preco, 'Kvalor', round(kvalor,2), 'Dvalor', round(dvalor,2), 'Acao', 'desativa bandeira')

            if (status == "vendido" and flagbuy == "green" and kvalor >= dvalor and dvalor > 20):
                status = "watch"
                referencia_watch = preco
                print('Data:', time.gmtime(data), 'Preco:', preco, 'Kvalor', round(kvalor,2), 'Dvalor', round(dvalor,2), 'Acao', 'ativacao da bandeira')

            if (status == "watch" and referencia_watch != 0 and preco/referencia_watch >= (1+percentual_compra)):
                action = "compra"
                valor_compra = preco
                data_compra = data
                kvalorCompra = kvalor
                dvalorCompra = dvalor
                flagbuy = "red"
                status = "comprado"
                print('Data:', time.gmtime(data), 'Preco:', preco, 'Kvalor', round(kvalor,2), 'Dvalor', round(dvalor,2), 'Acao', action)

            #START GAIN#
            if (flagsell == "red" and status == "comprado" and kvalor >= limite_inferior and kvalor <= limite_superior and preco/valor_compra >= (1+start_gain)):
                flagsell = "green"
                maximo_local = preco
                print('Data:', time.gmtime(data), 'Preco:', preco, 'Kvalor', round(kvalor,2), 'Dvalor', round(dvalor,2), 'Acao', 'inicio gain')

            if (flagsell == "green" and preco > maximo_local):
                    maximo_local = preco
                
            #STOP LOSS#
            if (status == "comprado" and preco/valor_compra <= (1-stop_loss)):
                action = "venda"
                valor_venda = preco
                data_venda = data
                kvalorVenda = kvalor
                dvalorVenda = dvalor
                percent = ((preco/valor_compra)-1)*100
                percentual.append(preco/valor_compra)
                flagsell = "red"
                status = "vendido"
                print('Data:', time.gmtime(data), 'Preco:', preco, 'Kvalor', round(kvalor,2), 'Dvalor', round(dvalor,2), 'Acao', 'venda stop loss','Percentual',round(((preco/valor_compra)-1)*100,2))

            #STOP GAIN#
            if (status == "comprado" and flagsell == "green" and preco/maximo_local <= (1-stop_gain)):
                action = "venda"
                valor_venda = preco
                data_venda = data
                kvalorVenda = kvalor
                dvalorVenda = dvalor
                percent = ((preco/valor_compra)-1)*100
                percentual.append(preco/valor_compra)
                flagsell = "red"
                status = "vendido"
                print('Data:', time.gmtime(data), 'Preco:', preco, 'Kvalor', round(kvalor,2), 'Dvalor', round(dvalor,2), 'Acao', 'venda stop gain','Percentual',round(((preco/valor_compra)-1)*100,2))

mult = 1
for x in percentual:
    mult *= x
    saldo *= x
print("\nFinalizado")
print("Percentual Acumulado:", round(mult*100-100,2),r"%")
print("Saldo inicial", saldo_inicial, " -- Saldo final:", round(saldo,2))
