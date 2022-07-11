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



print("START TRADING","(",dt.datetime.now(),")")
slack_webhook("START TRADING"+"("+str(dt.datetime.now())+")")

position = 0 # 0:None 1:buy 2:sell
amount = 0
rate_at=0

while True:
    # every 15minutes
    minute=0

    balance = util.get_balance_now(exchange)
    print("[EVERY15MINUTES] balance now: ",str(balance),"(",dt.datetime.now(),")")

    since_time=int(time.time()-15*13)*1000 # 現在のUNIX秒から60足分戻してmsに
    
    #ロウソク足を取得
    rate_df = pd.DataFrame(data=exchange.fetch_ohlcv(symbol=config.symbol,timeframe=config.timeframe,since=since_time,limit=13),columns=["timestamp","open","high","low","close","volume"])

    sma_short = util.make_sma(rate_df, 5) # 短期移動平均線を作成 ※期間についてはお好み
    sma_long = util.make_sma(rate_df, 13) # 長期移動平均線を作成 ※期間についてはお好み

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

    if position!=0: # ポジションを持ってないとき
        if golden_cross:
            amount = util.cal_amount(exchange)
            balance = util.get_balance_now(exchange)

            exchange.create_order(symbol=config.symbol, type='market', side='buy', amount=amount)
            rate_at = util.get_rate_now(exchange)
            position = 1
            print("[BUY] Captured golden cross!","(",dt.datetime.now(),")","\n  symbol: "+config.symbol+"\n  amount: "+str(amount)+"\n  rate: "+str(rate_at)+"\n  balance now: "+str(balance))
            slack_webhook("[BUY] Captured golden cross!"+"("+str(dt.datetime.now())+")"+"\n  symbol: "+config.symbol+"\n  amount: "+str(amount)+"\n  rate: "+str(rate_at)+"\n  balance now: "+str(balance))
        elif dead_cross:
            amount = util.cal_amount(exchange)
            balance = util.get_balance_now(exchange)

            exchange.create_order(symbol=config.symbol, type='market', side='sell', amount=amount)
            rate_at = util.get_rate_now(exchange)
            position = 2
            print("[SELL] Captured dead cross!","(",dt.datetime.now(),")","\n  symbol: "+config.symbol+"\n  amount: "+str(amount)+"\n  rate: "+str(rate_at)+"\n  balance now: "+str(balance))
            slack_webhook("[SELL] Captured dead cross! ("+str(dt.datetime.now())+")\n  symbol: "+config.symbol+"\n  amount: "+str(amount)+"\n  rate: "+str(rate_at)+"\n  balance now: "+str(balance))

    while minute<13:
        # every minute

        if position == 1: # 買ってたら
            rate_now = util.get_rate_now(exchange)
            change_rate = (rate_at/rate_now)*100
            if change_rate>102: # 2%以上の値上がりで利確
                exchange.create_order(symbol=config.symbol, type='market', side='sell', amount=amount,params={"reduceOnly":True})
                position = 0
                amount = 0
                rate_at = 0
                time.sleep(1)
                balance = util.get_balance_now(exchange)

                print("[PROFIT] Captured 2% UP","(",dt.datetime.now(),")","\n  balance now: "+str(balance))
                slack_webhook("[PROFIT] Captured 2% UP("+str(dt.datetime.now())+")\n  balance now: "+str(balance))

            elif change_rate<99: # 1%以上の値下がりで損切
                exchange.create_order(symbol=config.symbol, type='market', side='sell', amount=amount,params={"reduceOnly":True})
                position = 0
                amount = 0
                rate_at = 0

                time.sleep(1)
                balance = util.get_balance_now(exchange)

                print("[LOSS] Captured 1% DOWN","(",dt.datetime.now(),")","\n  balance now: "+str(balance))
                slack_webhook("[LOSS] Captured 1% DOWN("+str(dt.datetime.now())+")\n  balance now: "+str(balance))
            
        elif position ==2: # 売ってたら
            rate_now = util.get_rate_now(exchange)
            change_rate = (rate_at/rate_now)*100
            if change_rate<98: # 2%以上の値下がりで利確
                exchange.create_order(symbol=config.symbol, type='market', side='buy', amount=amount,params={"reduceOnly":True})
                position = 0
                amount = 0
                rate_at = 0

                time.sleep(1)
                balance = util.get_balance_now(exchange)

                print("[PROFIT] Captured 2% DOWN","(",dt.datetime.now(),")","\n  balance now: "+str(balance))
                slack_webhook("[PROFIT] Captured 2% DOWN("+str(dt.datetime.now())+")\n  balance now: "+str(balance))

            elif change_rate>101: # 1%以上の値上がりで損切
                exchange.create_order(symbol=config.symbol, type='market', side='buy', amount=amount,params={"reduceOnly":True})
                position = 0
                amount = 0
                rate_at = 0

                time.sleep(1)
                balance = util.get_balance_now(exchange)

                print("[LOSS] Captured 1% UP","(",dt.datetime.now(),")","\n  balance now: "+str(balance))
                slack_webhook("[LOSS] Captured 1% UP("+str(dt.datetime.now())+")\n  balance now: "+str(balance))

        time.sleep(1)
        minute+=1
        

#exchange.create_order(symbol=symbol, type='market', side='sell', amount=0.002)
#exchange.create_order(symbol=symbol, type='market', side='buy', amount=0.002,params={"reduceOnly":True})