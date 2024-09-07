from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import ta.trend as ta
import yfinance as yf

class YahooAPI:
    def __init__(self, ticker, period):
        self._ticker = ticker
        self._period = period
        self._data = self.fetch_data()

    @property
    def ticker(self):
        return self._ticker

    @ticker.setter
    def ticker(self, value):
        self._ticker = value
        self._data = None  # Invalidate the data when ticker changes

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, value):
        self._period = value
        self._data = None  # Invalidate the data when period changes

    def fetch_data(self):
        if not self._ticker or not self._period:
            raise ValueError("Both ticker and period must be set before fetching data")

        interval = self.get_interval(self._period)
        self._data = yf.download(self._ticker, period=self._period, interval=interval)

    def get_candlestick_data(self):
        if self._data is None:
            self.fetch_data()

        candlestick_data = [
            {
                'time': int(row.Index.timestamp()),
                'open': row.Open,
                'high': row.High,
                'low': row.Low,
                'close': row.Close
            }
            for row in self._data.itertuples()
        ]

        return candlestick_data
    
    def get_line_data(self):
        if self._data is None:
            self.fetch_data()

        line_data = [
            {
                'value': row.Close,
                'time': int(row.Index.timestamp())
                
            }
            for row in self._data.itertuples()
        ]

        return line_data

    def get_volume_data(self):
        if self._data is None:
            self.fetch_data()

        volume_data = [
            {
                'value': row.Volume,
                'time': int(row.Index.timestamp())
            }
            for row in self._data.itertuples()
        ]
        return volume_data

    @staticmethod
    def get_interval(period):
        intervals = {
            '1d': '1m',
            '5d': '5m',
            '1mo': '30m',
            '6mo': '1h',
            '1y': '1d',
            '5y': '1wk',
            'max': '1mo'
        }
        if period in intervals:
            return intervals[period]
        else:
            raise ValueError("Invalid period provided")
        

class IndicatorAPI:
    def __init__(self, data):
        self.data = data
    
    def sma(self):
        if 'close' not in self.data[0]:
            print()
            return {'error': 'Invalid input'}

        df = pd.DataFrame(self.data)
        sma_period = 20  # Fixed period for SMA
        sma_indicator = ta.SMAIndicator(close=df['close'], window=sma_period)
        df['sma'] = sma_indicator.sma_indicator()

        # Filter out NaN values
        df = df.dropna(subset=['sma'])

        sma_data = [
            {
                'value': row.sma,
                'time': row.time
            }
            for row in df.itertuples()
        ]
        return sma_data
    
    def ema(self):
        if 'close' not in self.data[0]:
            return {'error': 'Invalid input'}
        
        df = pd.DataFrame(self.data)
        
        ema_period = 14  # Fixed period for EMA (example)
        ema_indicator = ta.EMAIndicator(close=df['close'], window=ema_period)
        df['ema'] = ema_indicator.ema_indicator()
        
        # Filter out NaN values
        df = df.dropna(subset=['ema'])
        
        ema_data = [
            {'value': row.ema, 'time': row.time}
            for row in df.itertuples()
        ]
        
        return ema_data










    