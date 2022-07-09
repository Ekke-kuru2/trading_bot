import time
import ccxt
import json
import pandas as pd
#import matplotlib as mp
import sys,os

from slack import slack_webhook



# 単純移動平均線を算出
def make_sma(candles, span):
    return pd.Series(candles["close"]).rolling(window = span).mean()


exchange = ccxt.bybit()
exchange.apiKey = os.environ["BYBIT_APIKEY_TEST"]
exchange.secret = os.environ["BYBIT_SECRET_TEST"]
exchange.set_sandbox_mode(True)
crypto = 'BTC'
currency = 'USDT'
interval = 60
duration = 15#移動平均(大きいほう)のサイズ
trading_amount = 30

symbol = crypto + currency
position=0#いくら買ってるか
last_rate=0#買ったときの値

'''
ticker_info = exchange.fetch_ticker(symbol)
print(ticker_info)
ticker_balance = exchange.fetch_balance()
print(ticker_balance)
'''

slack_webhook("test")

#exchange.create_order(symbol=symbol, type='market', side='sell', amount=0.002)
#exchange.create_order(symbol=symbol, type='market', side='buy', amount=0.002,params={"reduceOnly":True})