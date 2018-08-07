import json
import websocket
import time
import requests
import sqlite3
import csv

arquivos = ['IOTUSD15m','IOTUSD30m','IOTUSD1h','IOTUSD3h','IOTUSD6h','IOTUSD12h','IOTUSD1D']


############ Parametros externos para Simulação ############

print("******* Simulação de Trade" "*******\n")
print("Digite os parâmetros a serem usados\n")


limite_inferior = int(input("Digite o limite inferior da região do gain: "))
limite_superior = int(input("Digite o limite superior da região do gain: "))
##start_gain = float(input("Digite o percentual para iniciar o gain - sem o símbolo %: "))/100
##stop_gain = float(input("Digite o percentual do recuo que para o gain - sem o símbolo %: "))/100
##stop_loss = float(input("Digite o percentual para STOP LOSS: "))/100
saldo = float(input("Digite o saldo inicial para simulação: "))
print("\nIniciando Simulação\n")
saldo_inicial = saldo
cont = 0

############################################################

for arquivo in arquivos:        

    for i in range(0,11):
        for j in range(1,11):
            for k in range(0,11):   
                with open('/home/ricardo/estudos/simulacoes/simulador/332411/'+arquivo+'.csv', newline ='') as csvfile:
                    reader = csv.DictReader(csvfile)

                    start_gain = (1+(i/10))/100
                    stop_gain = (j/10)/100
                    stop_loss = (1+(k/10))/100

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
                    
                    for row in reader:
                        data = int(row['data'])
                        preco = float(row['preco'])
                        quantidade = float(row['quantidade'])
                        tipo = str(row['tipo'])
                        kvalor = float(row['kvalor'])
                        dvalor = float(row['dvalor'])
                        fechamento = str(row['fechamento'])

                        if (status == "vendido" and flagbuy == "red" and kvalor < 20 and dvalor < 20):
                            flagbuy = "green"

                        if (status == "vendido" and flagbuy == "green" and kvalor >= dvalor and dvalor > 20):
                            action = "compra"
                            valor_compra = preco
                            data_compra = data
                            kvalorCompra = kvalor
                            dvalorCompra = dvalor
                            flagbuy = "red"
                            status = "comprado"
                            #writer.writerow({'data':data, 'preco':preco, 'kvalor':kvalor, 'dvalor':dvalor, 'acao':action, 'percentual':''})

                        #START GAIN#
                        if (flagsell == "red" and status == "comprado" and kvalor >= limite_inferior and kvalor <= limite_superior and preco/valor_compra >= (1+start_gain)):
                            flagsell = "green"
                            maximo_local = preco
                            #writer.writerow({'data':data, 'preco':preco, 'kvalor':kvalor, 'dvalor':dvalor, 'acao':'inicio gain','percentual':''})
                            #print("Start gain")

                        if (flagsell == "green" and preco > maximo_local):
                            maximo_local = preco
                            

                        #STOP LOSS#
                        if (status == "comprado" and preco/valor_compra <= (1-stop_loss)):
                            action = "venda"
                            valor_venda = preco
                            data_venda = data
                            kvalorVenda = kvalor
                            dvalorVenda = dvalor
                            #print(time.ctime(data_compra),valor_compra,kvalorCompra,dvalorCompra,time.ctime(data_venda), valor_venda,kvalorVenda,dvalorVenda, "Percentual:",round(((preco/valor_compra)-1)*100,2))
                            percent = ((preco/valor_compra)-1)*100
                            percentual.append(preco/valor_compra)
                            flagsell = "red"
                            status = "vendido"
                            #writer.writerow({'data':data, 'preco':preco, 'kvalor':kvalor, 'dvalor':dvalor, 'acao':'stop loss','percentual':round(((preco/valor_compra)-1)*100,2)})
                            #print("stop")

                        #STOP GAIN#
                        if (status == "comprado" and flagsell == "green" and preco/maximo_local <= (1-stop_gain)):
                            action = "venda"
                            valor_venda = preco
                            data_venda = data
                            kvalorVenda = kvalor
                            dvalorVenda = dvalor
                            #print(time.ctime(data_compra),valor_compra,kvalorCompra,dvalorCompra,time.ctime(data_venda), valor_venda,kvalorVenda,dvalorVenda, "Percentual:",round(((preco/valor_compra)-1)*100,2))
                            percent = ((preco/valor_compra)-1)*100
                            percentual.append(preco/valor_compra)
                            flagsell = "red"
                            status = "vendido"
                            #writer.writerow({'data':data, 'preco':preco, 'kvalor':kvalor, 'dvalor':dvalor, 'acao':'venda stop gain','percentual':round(((preco/valor_compra)-1)*100,2)})

                mult = 1
                for x in percentual:
                    mult *= x
                    saldo *= x

                with open('/home/ricardo/estudos/simulacoes/simulador/3377/'+arquivo+'_saida.csv',"a",newline="") as fw:
                    cw = csv.writer(fw,delimiter="\n")
                    fieldnames = ['startgain', 'stopgain','stoploss', 'resultado']
                    writer = csv.DictWriter(fw, fieldnames=fieldnames)
                    writer.writerow({'startgain':round(start_gain*100,2), 'stopgain':round(stop_gain*100,2),'stoploss': round(stop_loss*100,2), 'resultado':round(mult*100-100,2)})

                cont += 1
                print('Percentual concluído: ',round((cont/(1210*7))*100,2),r'%')
