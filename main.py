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


while True:
    # every 15minutes
    minute=0

    since_time=int(time.time()-60*15*60)*1000 # 現在のUNIX秒から60足分戻してmsに
    rate_df = pd.DataFrame(data=exchange.fetch_ohlcv(symbol=config.symbol,timeframe=config.timeframe,since=since_time,limit=60),columns=["timestamp","open","high","low","close","volume"])

    sma_5 = util.make_sma(rate_df, 30) # 短期移動平均線を作成 ※期間についてはお好み
    sma_13 = util.make_sma(rate_df, 60) # 長期移動平均線を作成 ※期間についてはお好み

    # 短期移動平均線 > 長期移動平均線 の状態が3本続いたらゴールデンクロス（騙し防止のために判断まで少し待つ）
    golden_cross = sma_5.iloc[-1] > sma_13.iloc[-1] \
        and sma_5.iloc[-2] > sma_13.iloc[-2] \
        and sma_5.iloc[-3] > sma_13.iloc[-3] \
        and sma_5.iloc[-4] < sma_13.iloc[-4]

    # 短期移動平均線 < 長期移動平均線 の状態が3本続いたらデッドクロス（騙し防止のために判断まで少し待つ）
    dead_cross = sma_5.iloc[-1] < sma_13.iloc[-1] \
        and sma_5.iloc[-2] < sma_13.iloc[-2] \
        and sma_5.iloc[-3] < sma_13.iloc[-3] \
        and sma_5.iloc[-4] > sma_13.iloc[-4]

    print(golden_cross,dead_cross)

    while minute<15:
        # every minute
        time.sleep(60)
        minute+=1
        

#exchange.create_order(symbol=symbol, type='market', side='sell', amount=0.002)
#exchange.create_order(symbol=symbol, type='market', side='buy', amount=0.002,params={"reduceOnly":True})