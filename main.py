import time
import ccxt
import json
import pandas as pd
#import matplotlib as mp
import sys,os

from slack import slack_webhook
from util import util
from config import config


exchange = ccxt.bybit()
exchange.apiKey = os.environ["BYBIT_APIKEY_TEST"]
exchange.secret = os.environ["BYBIT_SECRET_TEST"]
exchange.set_sandbox_mode(True)


print(util.cal_amount(exchange))

#slack_webhook("test")

'''
while True:
    minute=0
    while minute<15:

        time.sleep(60)
        minute+=1
        '''

#exchange.create_order(symbol=symbol, type='market', side='sell', amount=0.002)
#exchange.create_order(symbol=symbol, type='market', side='buy', amount=0.002,params={"reduceOnly":True})