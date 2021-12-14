from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import configparser

import random
import requests
import bs4
from bs4 import *
import json
app = Flask(__name__)


config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

def xmr_bot():
    #post_data="hashrate=100&powerConsumption=0&poolFee=0&currency=TWD&electricityCosts=0"
    xmr_post = {"hashrate":"10000","powerConsumption":"0","poolFee":"0","currency":"TWD","electricityCosts":"0"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    target_url = 'https://api.c3pool.com/miner/<miner address>/stats/allWorkers'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    j = json.loads(res.text)
    
    # hash
    payhash = j.get('global').get('hash2')
    int_payhash = int(payhash)/1000
    
    # rig_num
    num = len(j)
    
    xmr_url = 'https://www.whattomine.com/coins/101-xmr-randomx?hr={}&p=0&fee=1&cost=0&hcost=0.0&span_br=&span_d=24&commit=Calculate'.format(int(payhash))
    xmr_rs = requests.session()
    try:
        xmr_res = xmr_rs.get(xmr_url,headers=headers,verify=False)
        xmr_soup = BeautifulSoup(xmr_res.text, 'html.parser')
        print(int(payhash))
        test = xmr_soup.select('.text-end')
        price_list = []
        for data in xmr_soup.select('.text-end'):
            if "$" in data.text:
            	price = str(data.text).split()
            	price_list.append(price)

        day_price = "".join(price_list[7]).replace('$','')
        week_price = "".join(price_list[8]).replace('$','')
        month_price = "".join(price_list[11]).replace('$','')
	
        day_price = int(float(day_price)*27)
        week_price = int(float(week_price)*27)
        month_price = int(float(month_price)*27)
    except:
        pass
    content = "power:  " + str(int_payhash) + "  KH/s" + "\n" + "rig:  " + str(num) + "\n" + "day:  " + str(day_price) + "\n" + "week:  " + str(week_price) + "\n" + "month:  " + str(month_price)
    return content
    
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        print(body, signature)
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def pretty_echo(event):
    
    

    if "qq" in event.message.text:
        content = "dont cry"
        line_bot_api.reply_message(
	    event.reply_token,
	    TextSendMessage(text=content)
	)
        return 0
    
    if event.message.text == "xmr":
        content = xmr_bot()
        line_bot_api.reply_message(
	    event.reply_token,
	    TextSendMessage(text=content)
	)
        return 0

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)
