import json
import websocket
import time
import requests

pares = ['BCHBTC','BCHUSD','EOSBTC','EOSUSD','ETCBTC','ETCUSD','IOTBTC','IOTUSD','LTCBTC','LTCUSD']


def get_last(par):
    
    response = requests.get("https://api.bitfinex.com/v2/candles/trade:15m:t" + par + "/hist?limit=2")

    if response.status_code == 200:
        candles = json.loads(response.content.decode('utf-8'))        
       
    return candles[1][2]


def get_candle(par):

    response = requests.get("https://api.bitfinex.com/v2/candles/trade:15m:t" + par + "/hist?limit=100")

    if response.status_code == 200:
        candles = json.loads(response.content.decode('utf-8'))
        fechamentos = []

        for i in range(0,100):
            fechamentos.append(candles[i][2])

    return fechamentos

def calcula_rsi(fechamentos):
    rsi = []
    media_ganhos = 0
    media_perdas = 0
    perdas = []
    ganhos = []

    # cálculo do primeiro RSI    

    for i in range(0,7):
        dif = fechamentos[98-i]-fechamentos[99-i]        
        if dif >= 0:
            media_ganhos += dif
        if dif < 0:
            media_perdas += -1*dif

    media_ganhos = media_ganhos/7
    media_perdas = media_perdas/7

    relative = 100 - (100 / (1 + (media_ganhos / media_perdas)))

    rsi.append(relative)

    # cálculo do segundo RSI pra frente

    for i in range(0,92):
    
        dif = fechamentos[91-i] - fechamentos[92-i]

        if dif >= 0:
            media_ganhos = (media_ganhos*6 + dif) / 7
            media_perdas = (media_perdas*6) / 7
            
        else:
            media_ganhos = (media_ganhos*6) / 7
            media_perdas = (media_perdas*6 + (-1*dif)) / 7

        relative = 100 - (100 / (1 + (media_ganhos / media_perdas)))
        rsi.insert(0,relative)
    
        
    resultados = [rsi,media_ganhos,media_perdas]
    
    return resultados

def calcula_estocastico(rsi):
    stoch = []
    for i in range(0,87):
        stoch.insert(0,100*((rsi[86-i]-min(rsi[86-i:93-i])) / (max(rsi[86-i:93-i])-min(rsi[86-i:93-i]))))
    return stoch

def calcula_kvalor(stoch):
    kvalor = []
    for i in range(0,85):
        kvalor.insert(0,sum(stoch[84-i:87-i])/3)
    return kvalor


def calcula_dvalor(kvalores):
    dvalor = []
    for i in range(0,83):
        dvalor.insert(0,sum(kvalores[82-i:85-i])/3)
    return dvalor

def valores_pares(par):
    candle = get_candle(par)
    valores = calcula_rsi(candle)
    rsi = valores[0]
    media_ganhos = valores[1]
    media_perdas = valores[2]
    stoch = calcula_estocastico(rsi)
    kvalores = calcula_kvalor(stoch)
    dvalores = calcula_dvalor(kvalores)
    posicao = ""
    if (kvalores[0] < 20 and dvalores[0] < 20):
        posicao = "Em posicao de entrada"
    

    return ([par,candle[:7],rsi[:7],media_ganhos,media_perdas,stoch[:3],kvalores[:3],dvalores[0],posicao])

todosPares = []

for cadapar in pares:
    dadospar = valores_pares(cadapar)
    todosPares.append(dadospar)


for i in range(0,len(todosPares)):
    if (todosPares[i][7] <= 200):
        print ("Par",todosPares[i][0], "Valor do K:", round(todosPares[i][6][0],2), "Valor do D", round(todosPares[i][7],2), todosPares[i][8])

print("\n")
agora = int(time.time())
inicio = int(agora)//900*900
xsegundos = inicio + 901 - agora



while True:

    time.sleep(xsegundos)

    for i in range(0,len(todosPares)):
        preco = get_last(pares[i])
        todosPares[i][1].insert(0,0)
        todosPares[i][1].pop(-1)
        #todosPares[i][3].insert(0,0)
        #todosPares[i][3].pop(-1)
        #todosPares[i][4].insert(0,0)
        #todosPares[i][4].pop(-1)
        todosPares[i][2].insert(0,0)
        todosPares[i][2].pop(-1)
        todosPares[i][5].insert(0,0)
        todosPares[i][5].pop(-1)
        todosPares[i][6].insert(0,0)
        todosPares[i][6].pop(-1)

        #Atualiza os valores para os cálculos

        todosPares[i][1][0] = preco

        dif = todosPares[i][1][0] - todosPares[i][1][1]

        if dif >= 0:
           todosPares[i][3] = (todosPares[i][3]*6 + dif) / 7
           todosPares[i][4] = (todosPares[i][4]*6) / 7
            
        else:
           todosPares[i][3] = (todosPares[i][3]*6) / 7
           todosPares[i][4] = (todosPares[i][4]*6 + (-1*dif)) / 7


        relative = 100 - (100 / (1 + (todosPares[i][3] / todosPares[i][4])))

        todosPares[i][2][0] = relative

        todosPares[i][5][0] = 100*((todosPares[i][2][0]-min(todosPares[i][2][:7])) / (max(todosPares[i][2][:7])-min(todosPares[i][2][:7])))

        todosPares[i][6][0] = sum(todosPares[i][5][:3])/3

        dvalor = sum(todosPares[i][6][:3]) / 3

        posicao = ""

        if (todosPares[i][6][0] < 20 and dvalor < 20):
            posicao = "Em posicao de entrada"

        print ("Par:", todosPares[i][0], "Valor do K:", round(todosPares[i][6][0],2), "Valor do D:", round(dvalor,2))

        xsegundos = 901
