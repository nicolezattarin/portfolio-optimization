"""
get data from yahoo finance
"""
import pandas as pd
import yfinance as yf
from datetime import datetime

class DataSource:

    def __init__(self, symbols, start_date, end_date):
        # TODO: extend to multiple data sources
        # TODO: change timeframes (now only daily data is supported)
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        self.stats = None

    def get_data(self):
        self.data = {}
        for symbol in self.symbols:
            try:
                data = yf.download(symbol, start=self.start_date, end=self.end_date)
                self.data[symbol] = data
            except:
                print(f'Error downloading data for {symbol}')
                continue

    def get_stats(self):
        self.stats = pd.DataFrame()
    
        for symbol in self.symbols:
            s = {}
            s['mean_ret'] = self.data[symbol]['Adj Close'].pct_change().mean()*100
            s['std_ret'] = self.data[symbol]['Adj Close'].pct_change().std()*100
            s['sharpe'] = s['mean_ret'] / s['std_ret']
            s['annualized_sharpe'] = s['sharpe'] * (252**0.5)
            s['yearly_ret'] = self.data[symbol].resample('Y').last()['Adj Close'].pct_change().mean()*100
            s['yearly_std'] = self.data[symbol].resample('Y').last()['Adj Close'].pct_change().std()*100
            s['yearly_sharpe'] = s['yearly_ret'] / s['yearly_std']
            self.stats = pd.concat([self.stats, pd.DataFrame(s, index=[symbol])])

        # get correlation matrix
        self.corr_matrix = pd.DataFrame(columns=self.symbols, index=self.symbols)
        for i in self.symbols:
            for j in self.symbols:
                self.corr_matrix.loc[i,j] = self.data[i]['Adj Close'].pct_change().corr(self.data[j]['Adj Close'].pct_change())


    



   