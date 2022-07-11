import time
import ccxt
import json
import pandas as pd
import matplotlib as mp
import os
import datetime as dt

from slack import slack_webhook
from util import util
from config import config


exchange = ccxt.bybit()
exchange.apiKey = os.environ["BYBIT_APIKEY_TEST"]
exchange.secret = os.environ["BYBIT_SECRET_TEST"]
exchange.set_sandbox_mode(True)


while True:
    i=1
    since_time=int(time.time()-60*15*60-60*15*i)*1000 # 現在のUNIX秒から60足分戻してmsに
    
    #ロウソク足を取得
    rate_df = pd.DataFrame(data=exchange.fetch_ohlcv(symbol=config.symbol,timeframe=config.timeframe,since=since_time,limit=60),columns=["timestamp","open","high","low","close","volume"])

    sma_short = util.make_sma(rate_df, 30) # 短期移動平均線を作成 ※期間についてはお好み
    sma_long = util.make_sma(rate_df, 60) # 長期移動平均線を作成 ※期間についてはお好み
    print(sma_short)
    print(sma_long)

    '''
    # 短期移動平均線 < 長期移動平均線 が 短期移動平均線 > 長期移動平均線 になったらゴールデンクロス
    golden_cross = sma_short.iloc[-1] > sma_long.iloc[-1] 
        and sma_short.iloc[-2] < sma_long.iloc[-2] 

    # 短期移動平均線 > 長期移動平均線 が 短期移動平均線 < 長期移動平均線 になったらデッドクロス
    dead_cross = sma_short.iloc[-1] < sma_long.iloc[-1] 
        and sma_short.iloc[-2] > sma_long.iloc[-2] 
    print("  golden cross: ",golden_cross,"\n  dead cross: ",dead_cross)
    '''

    golden_cross = sma_short.iloc[-1] > sma_long.iloc[-1] \
            and sma_short.iloc[-2] > sma_long.iloc[-2] \
            and sma_short.iloc[-3] > sma_long.iloc[-3] \
            and sma_short.iloc[-4] < sma_long.iloc[-4]

    # 短期移動平均線 < 長期移動平均線 の状態が3本続いたらデッドクロス（騙し防止のために判断まで少し待つ）
    dead_cross = sma_short.iloc[-1] < sma_long.iloc[-1] \
        and sma_short.iloc[-2] < sma_long.iloc[-2] \
        and sma_short.iloc[-3] < sma_long.iloc[-3] \
        and sma_short.iloc[-4] > sma_long.iloc[-4]
    print(golden_cross,dead_cross)
    time.sleep(3)
    i+=1
