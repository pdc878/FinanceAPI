
#worth scare shoe seed devote sudden wife shy decorate present lobster asset

import websocket, json, pprint, requests
import pandas as pd
import numpy as np
import traderAPI
from ta.trend import PSARIndicator, MACD
import alpaca_trade_api as tradeapi

SOCKET = "wss://data.alpaca.markets/stream"


BASE_URL = "https://paper-api.alpaca.markets"


ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDER_URL = "{}/v2/orders".format(BASE_URL)
QUOTES_URL = "{}/v1/last_quote/"
HEADERS= {'APCA-API-KEY-ID': traderAPI.API_KEY, 'APCA-API-SECRET-KEY': traderAPI.SECRET_KEY}

RSI_PERIOD = 14
MACD_PERIOD = 26
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BIDU'
TRADE_QUANTITY = 50

bought_price = 1000
bought_price_macd = 1000
closes = []
highs= []
lows=[]
in_position = False
in_position_macd = False
in_position_bb = False
flag=-1

df = pd.DataFrame(columns=['ev','T','v','av','op','vw','o','c','h','l','a','s','e'])


def RSI(prices, n):
    deltas = np.diff(prices)
    seed = deltas[:n + 1]
    up = seed[seed >= 0].sum() / n
    down = -seed[seed < 0].sum() / n
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100. / (1. + rs)

    for i in range(n, len(prices)):
        delta = deltas[i - 1]  # The diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (n - 1) + upval) / n
        down = (down * (n - 1) + downval) / n

        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)

    return rsi


def SMA(period, values=None):
    values = closes if values is None else values

    """
    Simple Moving Average. Periods are the time frame. For example, a period of 50 would be a 50 day
    moving average. Values are usually the stock closes but can be passed any values
    """

    weigths = np.repeat(1.0, period)/period
    smas = np.convolve(values, weigths, 'valid')
    return smas  # as a numpy array


def EMA(period, values=None):
    values = closes if values is None else values

    """
    Exponential Moving Average. Periods are the time frame. For example, a period of 50 would be a 50 day
    moving average. Values are usually the stock closes but can be passed any values
    """

    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    a = np.convolve(values, weights, mode='full')[:len(values)]
    a[:period] = a[period]
    return a


def MACD(x, slow=26, fast=12):
    """
    Compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
    return value is emaslow, emafast, macd which are len(x) arrays
    """

    emaslow = EMA(slow, x)
    emafast = EMA(fast, x)
    return emaslow, emafast, emafast - emaslow

def BollingerBand(n=20, m=2):
    MA = SMA(n)

    BOLU = MA + m * np.std(closes[-n:])
    BOLD = MA - m * np.std(closes[-n:])

    return BOLD, BOLU

def order(symbol, qty, side, type, time_in_force):
    try:
        data = {
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": type,
            "time_in_force": time_in_force
        }
        print("sending order")
        requests.post(ORDER_URL, json=data, headers=HEADERS)

    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True



def on_open(ws):
    print('opened connection')

    auth_data = {
        "action": "authenticate",
        "data": {"key_id": traderAPI.API_KEY, "secret_key": traderAPI.SECRET_KEY}
    }

    ws.send(json.dumps(auth_data))

    listen_message = {"action": "listen", "data": {"streams": ["Q.BIDU"]}}

    ws.send(json.dumps(listen_message))

def on_close(ws):
    print('closed connection')



def on_message(ws, message):
    global closes,highs,lows, in_position,in_position_macd, bought_price, bought_price_macd, in_position_bb, flag



    print('received message')
    json_message = json.loads(message)
    pprint.pprint(json_message)
    global df

    with open('RECORDED_DATA.json','w') as outfile:
        json.dump(json_message['data'], outfile)


    #df.append(json_message['data'], ignore_index=True)

    with open('RECORDED_DATA.json') as json_file:
        df = json.load(json_file)

    candle = json_message['data']

    is_candle_closed = True

    close = candle['c']



    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes)


        psar = PSARIndicator(high=df['h'], low=df['l'], close=df['c'], step=0.02, max_step=0.2)

        candle['psar_down'] = psar.psar_down()
        candle['psar_up'] = psar.psar_up()

        # Add P SAR high indicator
        upind = psar.psar_up_indicator()

        # Add PSAR low indicator
        downind = psar.psar_down_indicator()

        print("PSAR VALUES:")
        print(upind)
        print(downind)

        if len(closes) > MACD_PERIOD:
            if upind[-1] > 0:
                if flag != 1:
                    order_succeeded_psar = order(TRADE_SYMBOL, TRADE_QUANTITY, 'buy', 'market', 'gtc')
                    flag = 1
                    print(order_succeeded_psar)

            elif downind[-1] > 0:
                if flag != 0:
                    order_succeeded_psar = order(TRADE_SYMBOL, TRADE_QUANTITY, 'sell', 'market', 'gtc')
                    flag = 0
                    print(order_succeeded_psar)


        if len(closes) > MACD_PERIOD:
            emaslow, emafast, macd = MACD(closes)

            print("all MACD calculated so far")
            print(macd)
            last_macd = macd[-1]
            print("the current MACD is {}".format(last_macd))

            if (0 < last_macd < 1):
                if not in_position_macd:
                    order_succeeded_macd = order(TRADE_SYMBOL, TRADE_QUANTITY, 'buy', 'market', 'gtc')
                    print(order_succeeded_macd)
                    bought_price_macd = closes[-1]
                    if order_succeeded_macd:
                        in_position_macd = True

            elif (-1 < last_macd < 0) or (last_macd >= (bought_price_macd*1.003)) or (last_macd <= (bought_price_macd*0.997)):
                if in_position_macd:
                    order_succeeded_macd = order(TRADE_SYMBOL, TRADE_QUANTITY, 'sell', 'market', 'gtc')
                    print(order_succeeded_macd)
                    if order_succeeded_macd:
                        in_position_macd = False


        if len(closes) > 20:
            BOLD, BOLU = BollingerBand()

            print("all Bollinger Bands calculated so far")
            print("Upper: ")
            print(BOLU)
            print("Lower: ")
            print(BOLD)
            last_BOLD = BOLD[-1]
            last_BOLU = BOLU[-1]

            print("the current BOLD is {}".format(last_BOLD))
            print("the current BOLU is {}".format(last_BOLU))

            if last_BOLU < closes[-1]:
                if in_position_macd:
                    order_succeeded_macd = order(TRADE_SYMBOL, TRADE_QUANTITY, 'sell', 'market', 'gtc')
                    print(order_succeeded_macd)
                    if order_succeeded_macd:
                        in_position_macd = False


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()