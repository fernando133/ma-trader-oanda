#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
import oandapyV20
from oandapyV20 import API
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.positions as positions

import configparser
import matplotlib.pyplot as plt

import oandapy as oanda
import time
import datetime

import numpy as np
import os

class MaTraderHelper:
    def __init__(cls, _ma_window, _instrument, _count, _granularity, _units_buy, _units_sell, _time_in_force, _loop_time_minutes):
        """
        Método construtor da classe, que recebe as variáveis
        globais de configuração
        """
        cls._ma_window              = _ma_window
        cls._instrument             = _instrument
        cls._count                  = _count
        cls._granularity            = _granularity
        cls._units_buy              = _units_buy
        cls._units_sell             = _units_sell
        cls._time_in_force          = _time_in_force
        cls._loop_time_minutes      = _loop_time_minutes
        cls._account_id             = 0;
        cls.client                  = None

    def get_connection(cls):
        """
        Configura um conexão com API OANDA
        """
        try:
            config = configparser.ConfigParser()
            config.read(u'config/config.ini')
            cls.account_id = config['oanda']['account_id']
            api_key = config['oanda']['api_key']
            cls.client = API(access_token=api_key)
            return cls.client
        except Exception, e:
                print "Trying to connect to API.: (error) .:", str(e)

    def get_dataframe(cls, resp):
        """
        Tranforma uma determinada resposta da API
        em um pandas dataframe.
        """
        dat = []
        for oo in resp.response['candles']:
            dat.append([oo['time'], oo['mid']['o'], oo['mid']['h'], oo['mid']['l'], oo['mid']['c'], oo['volume']])
        df = pd.DataFrame(dat)
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = df.set_index('Time')
        return df

    def get_loop_time(cls):
        """
        Calcula o tempo do loop principal do processo em minutos
        conforme parametro inicial de configuração: _loop_time_minutes.
        """
        return cls._loop_time_minutes * 60

    def running_mean(cls, x, N):
        """
        Executa o cálculo da média móvel para um
        conjunto de dados x, conforme uma
        janela de período N.
        """
        cumsum = np.cumsum(np.insert(x, 0, 0))
        return (cumsum[N:] -  cumsum[:-N]) / float(N)

    def buy_or_sell(cls, close_price, moving_average):
        """
        Conforme as colunas os valores de preço de fechamento
        e média móvel informados, retorna 0 ou 1 como sinal
        para compra ou venda. Sendo que 0 = venda e 1 = compra.
        """
        if moving_average > close_price:
            return 0
        else:
            return 1

    def run_moving_average(cls, df):
        """
        Executa o calculo da média móvel para um dado dataframe,
        conforme um valor informando na váriavel global de
        configuração _ma_window. Ex.: _ma_window = 30.
        """
        close =[]
        close = df.Close
        close_values = []
        for i in close:
            close_values.append(float(i))

        for index, item in enumerate(close_values):
            close_values[index] = float(item)
            
        moving_average = cls.running_mean(close_values, cls._ma_window)
        diff = len(df.index) - moving_average.size

        array_diff = []
        for i in range(diff):
            array_diff.append(0)
            
        result_y = []
        result_y.extend(array_diff)
        result_y.extend(moving_average)
        result_y = np.asarray(result_y)
        df['MA'] = result_y
        
        buy_sell = []
        for i in range(len(df.index)):
            buy_sell.append(cls.buy_or_sell(float(df.Close[i]), float(df.MA[i])))

        df['Buy_Sell'] = buy_sell
        last_action = df['Buy_Sell'][len(df['Buy_Sell'])-1]
        
        return df, last_action

    def buy(cls, _start, low):
        """
        Monta e executa uma negociação de compra.
        recebe o preço mais baixo do momento para
        calcular a limitação de perca da negociação.
        """
        low = float('{:.4f}'.format(low-(low*0.02)))

        order_buy = {
            "order": {
                "units": cls._units_buy,
                "instrument": cls._instrument,
                "timeInForce": 'FOK',
                "type": "MARKET",
                "positionFill": "DEFAULT",
                "stopLossOnFill": {
                    "price": str(low).decode('utf8')
                }
            }
        }
        
        print ("STOP LOSS: ", low)
        if _start == 1:
            r = orders.OrderCreate(cls.account_id, data=order_buy)
            print cls.client.request(r)
            _start=_start+1
        else:
            r = orders.OrderCreate(cls.account_id, data=order_buy)
            print cls.client.request(r)
            time.sleep(1)
            r = orders.OrderCreate(cls.account_id, data=order_buy)
            print cls.client.request(r)
            
        return _start, 'BUY'

    def sell(cls, _start, high):
        """
        Monta e executa uma negociação de venda.
        recebe o preço mais alto do momento para
        calcular a limitação de perca da negociação.
        """
        high = float('{:.4f}'.format(high+(high*0.02)))

        order_sell = {
            "order": {
                "units": cls._units_sell,
                "instrument": cls._instrument,
                "timeInForce": 'FOK',
                "type": "MARKET",
                "positionFill": "DEFAULT",
                "stopLossOnFill": {
                    "price": str(high).decode('utf8')
                }
            }
        }

        print ("STOP LOSS: ", high)
        if _start == 1:
            r = orders.OrderCreate(cls.account_id, data=order_sell)
            print cls.client.request(r)
            _start=_start+1
        else:
            r = orders.OrderCreate(cls.account_id, data=order_sell)
            print cls.client.request(r)
            time.sleep(1)
            r = orders.OrderCreate(cls.account_id, data=order_sell)
            print cls.client.request(r)
        
        return _start, 'SELL'

    def switch_global_action(cls, last_action, global_action, 
                                    start, high, low):
        """
        Verifica a cada instante qual foi a última ação e
        qual é a ação atual para que possa tomar as
        decisões de ficar em stand-by, comprar ou vender.
        """
        if(global_action == last_action):
            print "STAND BY"
            
        elif(global_action != last_action):
            pass
        
        if (global_action == 0 and last_action == 1):
            start, actual_action = cls.buy(start, low)
            print actual_action
            global_action = last_action
            
        if (global_action == 1 and last_action ==0):
            
            start, actual_action = cls.sell(start, high)
            print actual_action
            global_action = last_action
            
        return start, global_action

    def sync(cls):
        """
        Método responsável por sincronizar o tempo de início
        do processo com o tempo da API para que os dados
        obtidos sejam consistentes para a tomada de decisões.
        """
        print "Sincronizando..."
        t = datetime.datetime.utcnow()
        sleeptime = cls._loop_time_minutes*60 - (t.second + t.microsecond/1000000.0)
        time.sleep(sleeptime)
        return 1

    def get_response(cls):
        """
        Método responsável por obter dados históricos da API
        conforme uma quantidade de períodos e granularidade informada.
        Ex.: _count = 1000, _granularity = 'M15',
        para mais definições, consultar:
        http://developer.oanda.com/rest-live-v20/instrument-df/
        
        CandlestickGranularity
        """
        params = {
            "count": cls._count,
            "granularity": cls._granularity}
        return instruments.InstrumentsCandles(instrument=cls._instrument, params=params)

    def loop_request(cls, client):
        """
        Retorna uma resposta de uma requisição para API,
        de um determinado instante, conforme uma
        granularidade informada.
        """
        _candle_params = {
            "count": 1,
            "granularity": cls._granularity}
        while (True):
            try:
                r = instruments.InstrumentsCandles(instrument=cls._instrument,
                                           params=_candle_params)
                client.request(r)
                return r
            except Exception, e:
                print "Trying to get data.: (error) .:", str(e)
                cls.sync()

    def get_instant_df(cls, resp, df):
        """
        Conforme uma resposta do instante e um dataframe
        informados, adiciona a resposta e retira o
        registro mais antigo do dataframe, retornando
        o dataframe atualizado, o preço atual,
        o preço mais baixo e o preço mais alto do momento.
        """
        dat = []
        for oo in resp.response['candles']:
            dat.append([oo['time'], oo['mid']['o'], oo['mid']['h'], oo['mid']['l'], oo['mid']['c'], oo['volume']])

        data_frame = pd.DataFrame(dat)
        data_frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        data_frame = data_frame.set_index('Time')
        
        df = df.iloc[1:]
        df = df.append(data_frame)
        
        price      = float(df['Close'].iloc[-1])
        low_price  = float(df['Low'].iloc[-1])
        high_price = float(df['High'].iloc[-1])
        
        return df, price, low_price, high_price

    def start_wait(cls, start_hour, start_minute):
        """
        Define a hora inicio da execução do processo
        conforme hora e minuto informados
        """
        #print "A execução iniciará as ", start_hour, ":", start_minute,"h"
        while(True):
            dt = datetime.datetime.now()
            print "A execução iniciará as ", start_hour, ":", start_minute,"h"
            print "[Sincronizando..]", dt.hour, ":", dt.minute, ":", dt.second
            time.sleep(1)
            clear = lambda: os.system('clear')
            clear()
            if dt.hour == start_hour and dt.minute == start_minute:
                print "[Iniciando execução...]\n"
                break

    def set_end_process(cls, end_hour, end_minute):
        """
        Determina o fim do processo conforme hora e minuto
        informados
        """
        dt = datetime.datetime.now()
        if dt.hour == end_hour and dt.minute == end_minute:
            print "[Finalizando execução...]\n"
            return True
        return False

    def start(cls, start_hour, start_minute):
        """
        Método de início do processo, obtendo dados
        e calculando a primeira média móvel,
        retorna o cliente de acesso a API, o dataframe inicial,
        a ação global e atual.
        """
        #cls.sync()
        cls.start_wait(start_hour, start_minute)
        client = cls.get_connection()
        r = cls.get_response()
        client.request(r)
        df = cls.get_dataframe(r)
        df, last_action = cls.run_moving_average(df)
        global_action = df['Buy_Sell'][len(df['Buy_Sell'])-1]
        actual_action = ""
        return df, global_action, actual_action, client
