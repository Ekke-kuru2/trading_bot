import pandas as pd
import ccxt
from config import config

class util():
    @staticmethod
    def make_sma(candles, span):
        return pd.Series(candles["close"]).rolling(window = span).mean()

    @staticmethod
    def cal_amount(exchange:ccxt.bybit):
        ticker_info = exchange.fetch_ticker(config.symbol)
        ticker_balance = exchange.fetch_balance()
        return ticker_balance["free"]["USDT"]*config.leverage/ticker_info["close"]/2

        
        
