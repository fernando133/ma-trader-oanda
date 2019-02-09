#!/usr/bin/python
# -*- coding: utf-8 -*-
from helpers.ma_trader_helper import MaTraderHelper
import time
import sys

print 'Argument List:', str(sys.argv)
arguments          = sys.argv
_instrument        = arguments[1]
_granularity       = arguments[2]
_loop_time_minutes = int(arguments[3])
_ma_window         = int(arguments[4])
_start_hour        = int(arguments[5])
_start_minute      = int(arguments[6])
_end_hour          = int(arguments[7])
_end_minute        = int(arguments[8])

_count             = 1000
_units_buy         = '1000'
_units_sell        = '-1000'
_time_in_force     = 'FOK'

def watchdog():
    '''
    Dá inicio ao processo de verificação contínua
    e tomada de decisões.
    '''
    start = 1
    ma_trader = MaTraderHelper(_ma_window, _instrument, _count, _granularity, 
                                            _units_buy, _units_sell, _time_in_force, _loop_time_minutes)

    df, global_action, actual_action, client = ma_trader.start(_start_hour, _start_minute)
    while (True):
        r = ma_trader.loop_request(client)
        df, price, low_price, high_price = ma_trader.get_instant_df(r, df)
        df, last_action = ma_trader.run_moving_average(df)
        start, global_action = ma_trader.switch_global_action(last_action, global_action, start, low_price, high_price)
        print start, _instrument, _granularity, "MA:",_ma_window, global_action, last_action, "P.:",price,"L.:",low_price,"H.:",high_price
        print "\n"
        time.sleep(ma_trader.get_loop_time())

try:
    watchdog()
except Exception, e:
    print "O processo foi interrompido .: (ERRO): ", str(e)
