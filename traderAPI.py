import requests,json


API_KEY = "PKMW0WZ4QTTB5MFD68YN"
SECRET_KEY = "mjDWvW5KhqR2KxrDC0V4YR3PPqIVfxDRPa5SQILt"

BASE_URL = "https://paper-api.alpaca.markets"

ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDER_URL = "{}/v2/orders".format(BASE_URL)
HEADERS= {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}

BARS_URL = "https://data.alpaca.markets/v1/bars"





def getaccount():
    r = requests.get(ACCOUNT_URL, headers=HEADERS)

    return json.loads(r.content)

def createorder(symbol, qty, side, type, time_in_force):
    data={
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": type,
        "time_in_force": time_in_force
    }
    r = requests.post(ORDER_URL, json=data,headers=HEADERS)
    return json.loads(r.content)

