from django.conf import settings

from linebot import LineBotApi, WebhookParser
from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction
import os, json, requests

channel_secret = os.getenv('LINE_CHANNEL_SECRET', 'b7ce414421df207a4f7c49f185e0c5b0')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'A8rE0YCtMEEEr8898I+q25D4JXXD5eGMOc88ANFS7JdxKw5b0yxHN26SNeZRBlv44NWRLkbCjwtmAkeAEeWp8gKnBapOcaCrTyyfwsKEyGzZeFE179ccm8GCqyGeXiCj7K7DflhBwM2+m5icbqiojQdB04t89/1O/w1cDnyilFU=')
line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

def crawler(event):

    r = requests.post(
    'https://portal.sw.nat.gov.tw/APGQ/GB321!query',
    {
    'transType' : 'A',
    'mawb' : '',
    'hawb' : '40091824126158',
    },
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'}
    )

    list_of_dicts = r.json()
    #print(type(r))
    num = 0
    if list_of_dicts['msg'] == '[執行成功]':
        num = len(list_of_dicts['gridModel'])
        for i in range(0,num):
            data_date = list_of_dicts['gridModel'][i]
            data_date = data_date['proDate']
            data_time = list_of_dicts['gridModel'][i]
            data_time = data_time['proTime']
            data_type = list_of_dicts['gridModel'][i]
            data_type = data_type['proType']
            retxt = 'Date : {} time : {} type : {}'.format(data_date,data_time,data_type)
            line_bot_api.reply_message(event.reply_token, retxt)
    else:
        retxt = list_of_dicts['msg']
        line_bot_api.reply_message(event.reply_token, retxt)

