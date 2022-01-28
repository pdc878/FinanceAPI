#BF85UZAN7V2IPQ7Y
#VINTAGE API KEY


from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import csv
from ta.volatility import BollingerBands
from ta.trend import PSARIndicator, MACD

from alpha_vantage.timeseries import TimeSeries
import yfinance as yf



RSI_PERIOD = 14
MACD_PERIOD = 26
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BIDU'
TRADE_QUANTITY = 50

bought_price = 1000
bought_price_macd = 1000
closes = []
in_position = False
in_position_macd = False
in_position_bb = False


"""
Prices Read
"""

key = 'BF85UZAN7V2IPQ7Y'

ts = TimeSeries(key, output_format='pandas')
df, meta = ts.get_intraday('BIDU', interval='1min',outputsize='full')

df['TradeDate'] = df.index.date
df['time'] = df.index.time

market = df.between_time('09:30:00','16:00:00').copy()
market.sort_index(inplace=True)

market.info()



plt.figure(figsize=(12.2, 4.5))
plt.plot(df['4. close'], label='Close')
plt.xticks(rotation=45)
plt.title('Closing Prices History')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()



"""
BUY SELL LOGIC
"""
def buy_sell_bb(lower, upper):
    global df

    Buy=[]
    Sell=[]

    BuyShares = []
    SellShares = []

    flag=-1

    prevsharebuy = None

    for i in range(0,len(lower)):

        sharebuy = int(20000/df['4. close'][i])

        if lower[i] > 0:
            Sell.append(np.nan)
            SellShares.append(np.nan)
            if flag != 1:
                Buy.append(df['4. close'][i])
                BuyShares.append(df['4. close'][i] * sharebuy)
                flag = 1
                prevsharebuy=sharebuy
            else:
                Buy.append(np.nan)
                BuyShares.append(np.nan)
        elif (upper[i] > 0 and prevsharebuy is not None):
            Buy.append(np.nan)
            BuyShares.append(np.nan)
            if flag != 0:
                Sell.append(df['4. close'][i])
                SellShares.append(df['4. close'][i] * prevsharebuy)
                flag = 0
            else:
                Sell.append(np.nan)
                SellShares.append(np.nan)
        else:
            Buy.append(np.nan)
            BuyShares.append(np.nan)
            Sell.append(np.nan)
            SellShares.append(np.nan)


    return (Buy, Sell,SellShares,BuyShares)


"""
BUY SELL LOGIC
"""
def buy_sell_psar(up, down):
    global df

    Buy=[]
    Sell=[]

    BuyShares=[]
    SellShares=[]

    flag=-1

    prevsharebuy = None

    for i in range(0,len(up)):

        sharebuy = int(20000/(df['4. close'][i]))



        if up[i] > 0:
            Sell.append(np.nan)
            SellShares.append(np.nan)
            if flag != 1:
                Buy.append(df['4. close'][i])
                BuyShares.append(df['4. close'][i]*sharebuy)
                flag = 1
                prevsharebuy = sharebuy
            else:
                Buy.append(np.nan)
                BuyShares.append(np.nan)

        elif (down[i] > 0 and prevsharebuy is not None):
            Buy.append(np.nan)
            BuyShares.append(np.nan)
            if flag != 0:
                Sell.append(df['4. close'][i])
                SellShares.append(df['4. close'][i]*prevsharebuy)
                flag = 0
            else:
                Sell.append(np.nan)
                SellShares.append(np.nan)
        else:
            Buy.append(np.nan)
            BuyShares.append(np.nan)
            Sell.append(np.nan)
            SellShares.append(np.nan)


    return (Buy, Sell, SellShares,BuyShares)



def buy_sell_macd(diff):
    global df

    Buy=[]
    Sell=[]

    flag=-1

    BuyShares = []
    SellShares = []

    prevsharebuy = None

    for i in range(0,len(diff)):

        sharebuy = int(20000 / df['4. close'][i])

        if diff[i] > 0:
            Sell.append(np.nan)
            SellShares.append(np.nan)

            if flag != 1:
                Buy.append(df['4. close'][i])
                BuyShares.append(df['4. close'][i] * sharebuy)
                flag = 1
                prevsharebuy = sharebuy
            else:
                Buy.append(np.nan)
                BuyShares.append(np.nan)
        elif (diff[i] < 0 and prevsharebuy is not None):
            Buy.append(np.nan)
            BuyShares.append(np.nan)
            if flag != 0:
                Sell.append(df['4. close'][i])
                SellShares.append(df['4. close'][i] * prevsharebuy)
                flag = 0
            else:
                Sell.append(np.nan)
                SellShares.append(np.nan)
        else:
            Buy.append(np.nan)
            BuyShares.append(np.nan)
            Sell.append(np.nan)
            SellShares.append(np.nan)


    return (Buy, Sell,SellShares,BuyShares)



"""
TOTAL PROFIT LOGIC
"""
def totalProfits(buy, sell):

    nan_array = np.isnan(buy)
    not_nan_array = ~ nan_array
    buy = buy[not_nan_array]

    nan_array = np.isnan(sell)
    not_nan_array = ~ nan_array
    sell = sell[not_nan_array]

    if len(sell) > len(buy):
        tsell = sum(sell) - sell[0]
    else:
        tsell = sum(sell)

    if len(buy) > len(sell):
        tbuy = sum(buy) - buy[-1]
    else:
        tbuy = sum(buy)

    totalprof = tsell - tbuy

    totalprofpercent = (totalprof/20000)*100

    return totalprof,totalprofpercent



def printplot(buy,sell):
    plt.figure(figsize=(12.2, 4.5))
    plt.scatter(df.index, df['Buy_BB'], color='green', label='Buy', marker='^', alpha=1)
    plt.scatter(df.index, df['Sell_BB'], color='red', label='Sell', marker='v', alpha=1)
    plt.plot(df['4. close'], label='Close Price', alpha=0.35)
    plt.title('Buy and Sell')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.show()




if __name__ == "__main__":

    bb_ind = BollingerBands(close=df['4. close'], window=20, window_dev=2)

    df['bb_bbm'] = bb_ind.bollinger_mavg()
    df['bb_bbh'] = bb_ind.bollinger_hband()
    df['bb_bbl'] = bb_ind.bollinger_lband()

    # Add Bollinger Band high indicator
    df['bb_bbhi'] = bb_ind.bollinger_hband_indicator()

    # Add Bollinger Band low indicator
    df['bb_bbli'] = bb_ind.bollinger_lband_indicator()

    a = buy_sell_bb(df['bb_bbhi'],df['bb_bbli'])
    df['Buy_BB'] = a[0]
    df['Sell_BB'] = a[1]
    df['Sell_BB_Shares'] = a[2]
    df['Buy_BB_Shares'] = a[3]

    printplot(df['Buy_BB'], df['Sell_BB'])

    total = totalProfits(df['Buy_BB_Shares'], df['Sell_BB_Shares'])
    print("BB")
    print(total[0])
    print("BB Percent")
    print(str(total[1]) + '%')

    psar = PSARIndicator(high=df['2. high'],low=df['3. low'],close=df['4. close'], step=0.02, max_step=0.2)

    df['psar_down'] = psar.psar_down()
    df['psar_up'] = psar.psar_up()

    # Add P SAR high indicator
    df['psar_u'] = psar.psar_up_indicator()

    # Add PSAR low indicator
    df['psar_d'] = psar.psar_down_indicator()

    a = buy_sell_psar(df['psar_u'], df['psar_d'])
    df['Buy_PSAR'] = a[0]
    df['Sell_PSAR'] = a[1]
    df['Buy_PSAR_Shares'] = a[3]
    df['Sell_PSAR_Shares'] = a[2]

    printplot(df['Buy_PSAR'], df['Sell_PSAR'])

    total = totalProfits(df['Buy_PSAR_Shares'], df['Sell_PSAR_Shares'])
    print("PSAR")
    print(total[0])
    print("PSAR Percent")

    print(str(total[1]) + "%")



    macd = MACD(close=df['4. close'], window_slow=26, window_fast=12, window_sign=9)

    df['macd_dif'] = macd.macd_diff()

    a = buy_sell_macd(df['macd_dif'])
    df['Buy_macd'] = a[0]
    df['Sell_macd'] = a[1]
    df['Buy_macd_Shares'] = a[3]
    df['Sell_macd_Shares'] = a[2]

    printplot(df['Buy_macd'],df['Sell_macd'])

    total = totalProfits(df['Buy_macd_Shares'], df['Sell_macd_Shares'])
    print("MACD")
    print(total[0])
    print("MACD Percent")
    print(str(total[1]) + '%')




#8.1 -> 190

