from flask import Flask
from flask import request
from flask import jsonify
from flask_sslify import SSLify
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import requests
import json
import re

app = Flask(__name__)
sslify = SSLify(app)

TOKEN = 'your bot token'

#Добавление webhhok
#https://api.telegram.org/bot{TOKEN}/setWebhook?url=https://{your host}.pythonanywhere.com/

#удаление webhook
#https://api.telegram.org/bot{TOKEN}/deleteWebhook

#запрос информации о webhook
#https://api.telegram.org/bot{TOKEN}/getWebhookInfo

URL = f'https://api.telegram.org/bot{TOKEN}/'
url_coinmarket = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
COINMARKET_API_KEY = 'YOUR KEY'

headers = {
  'Accepts': 'application/json',
  'Accept-Encoding': 'deflate, gzip',
  'X-CMC_PRO_API_KEY': '{COINMARKET_API_KEY}',
  }

def crypto(symbol):
  session = Session()
  session.headers.update(headers)
  try:
    response = session.get(url_coinmarket, params={'symbol' : symbol})
    data = json.loads(response.text)
    price = data["data"][symbol]["quote"]["USD"]["price"]
    percent_change_24h = data["data"][symbol]["quote"]["USD"]["percent_change_24h"]
    market_cap_dominance = data["data"][symbol]["quote"]["USD"]["market_cap_dominance"]
  except Exception:
    return [0, 0, 0]
  return [price, percent_change_24h, market_cap_dominance]

def parse_text(text):
    pattern = r'/\w+'
    if re.search(pattern, text):
        return re.search(pattern, text).group().upper()[1:]
    return ''

def round_price(data):
    x = 0
    price = data[0]
    if price > 1000:
        return round(price)
    elif price >= 100 and price < 1000:
        x = 1
    elif price >= 10 and price < 100:
        x = 2
    elif price >= 1 and price < 10:
        x = 3
    elif price >= 0.1 and price < 1:
        x = 4
    elif price >= 0.01 and price < 0.1:
        x = 5
    elif price < 0.01:
        x = 6
    return round(price, x)

def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def sendmessage(chat_id, text='testing'):
    url = URL + 'sendmessage'
    answer = {
        'chat_id': chat_id,
        'text': text
    }
    req = requests.post(url, json=answer)
    return req.json()

@app.route('/', methods=['POST', 'GET'])
def index():
  if request.method == 'POST':
    r = request.get_json()
    try:
        chat_id = r['message']['chat']['id']
        message = r['message']['text']
        write_json(r)
    except Exception:
        message = 'Error'
        sendmessage(chat_id, message)


    symbol = parse_text(message)
    if symbol != '':
        data = crypto(symbol)
        price = round_price(data)
        if price != 0:
            text = f'*** {symbol} *** price is   {price} $,\nChange24h:   {round(data[1], 2)} %,\nMarket cap:   {round(data[2], 2)} %'
            sendmessage(chat_id, text)

    return jsonify(r)

  else:
    return '<h1>Arkadzzz wellcomes you</h1>'

  

if __name__ == '__main__':
    app.run()