import yfinance as yf
from gtts import gTTS
import datetime
from jinja2 import Environment, FileSystemLoader
import os
import json

tickers = yf.Tickers("^GSPC, ^FTSE")

# build tele-script
date=str(datetime.datetime.now().strftime("%A, %d %b"))
script="As of {date}, "

for index, ticker in tickers.tickers.items():
    longName=ticker.info.get('longName')
    hist=ticker.history(period="2d")

    percentChange=round(hist['Close'].pct_change().values[1]*100, 2)
    status = 'up' if percentChange > 0 else 'down'

    script += f"The {longName} is {status} by {percentChange} percent."

# generate mp3
date=str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"))
gTTS(text=script, lang='en').save(f"../mp3/{date}.mp3")

# update storage
with open('../local_storage.json', 'r') as file:
    json_data = file.read()

podcasts = json.loads(json_data)
podcasts.append({
    'title': date,
    'filename': f"{date}.mp3",
    'datetime': str(datetime.datetime.now().strftime("%A, %d %b %Y %H:%M GMT")), 
    'size': os.stat(f"../mp3/{date}.mp3").st_size
})

json_data = json.dumps(podcasts)
with open('../local_storage.json', 'w') as file:
    file.write(json_data)

# update index.html
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template("index.template.html")
template.stream(podcasts=podcasts).dump('../index.html')

# publish rss
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template("podcasts.template.rss")
template.stream(podcasts=podcasts).dump('../podcasts.rss')