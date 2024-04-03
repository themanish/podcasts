import yfinance as yf
from gtts import gTTS
from datetime import date
from jinja2 import Environment, FileSystemLoader
import os
import json

tickers = yf.Tickers("^GSPC, ^FTSE")

script=""

for index, ticker in tickers.tickers.items():
    longName=ticker.info.get('longName')
    hist=ticker.history(period="2d")

    percentChange=round(hist['Close'].pct_change().values[1]*100, 2)
    status = 'up' if percentChange > 0 else 'down'

    script += f"The {longName} is {status} by {percentChange} percent."

date=str(date.today())
gTTS(text=script, lang='en').save(f"../mp3/{date}.mp3")



with open('../local_storage.json', 'r') as file:
    json_data = file.read()

podcasts = json.loads(json_data)
podcasts.append({'date': date, 'size': os.stat(f"../mp3/{date}.mp3").st_size})

json_data = json.dumps(podcasts)
with open('../local_storage.json', 'w') as file:
    file.write(json_data)

# publish rss
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template("podcasts.template.rss")
template.stream(podcasts=podcasts).dump('../podcasts.rss')