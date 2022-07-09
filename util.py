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
        return ticker_balance["free"][config.currency]*config.leverage/ticker_info["close"]/2
    
    @staticmethod
    def get_rate_now(exchange):
        ticker_info = exchange.fetch_ticker(config.symbol)
        return ticker_info["close"]

    @staticmethod
    def get_balance_now(exchange):
        ticker_balance = exchange.fetch_balance()
        return ticker_balance["free"][config.currency]
        
        
