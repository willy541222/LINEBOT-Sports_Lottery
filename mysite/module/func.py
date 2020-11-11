from django.conf import settings

from linebot import LineBotApi, WebhookParser
from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction, TemplateSendMessage, ConfirmTemplate, MessageTemplateAction, PostbackTemplateAction
import os, json, requests
import math
import decimal
import variable_settings as varset
import urllib.parse
channel_secret = os.getenv('LINE_CHANNEL_SECRET', 'b7ce414421df207a4f7c49f185e0c5b0')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'A8rE0YCtMEEEr8898I+q25D4JXXD5eGMOc88ANFS7JdxKw5b0yxHN26SNeZRBlv44NWRLkbCjwtmAkeAEeWp8gKnBapOcaCrTyyfwsKEyGzZeFE179ccm8GCqyGeXiCj7K7DflhBwM2+m5icbqiojQdB04t89/1O/w1cDnyilFU=')
line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

#切換模式
def Togglemode(event, mode, userid):
    try:
        if mode =='high':
            mode = 'no'
            mode1 = '低賠率'
        else:
            mode = 'high'
            mode1 = '高賠率'
        varset.set(userid, mode)
        message = TextSendMessage(
            text = '模式設定為 : ' + mode1
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text = 'Error !'))

#計算本金賠率
def send_calc(event, mode, mtext):
    datalist = mtext.split('/')
    try:
        if mode == 'high':
            high_principle = int(datalist[0])
            high_odds = int(datalist[1])
            #計算出低賠本金
            low_principle = high_principle * (high_odds -1)

            #無條件捨去，因為一注為10元
            b = low_principle % 10
            if int(b) != 9:
                low_principle = low_principle - b
            else:
                low_principle = low_principle - b + 10

            #計算出最少低賠率
            low_odds = high_principle / low_principle + 1
            buy_low_odds =  decimal.Decimal(low_odds).quantize(decimal.Decimal('0.01'),rounding=decimal.ROUND_UP)

            text1 = "現在的模式為高賠率換算低賠率"
            text1 += "\n高賠率本金 : " + high_principle
            text1 += "\n高賠率為 : " + high_odds
            text1 += "\n低賠率本金為 : " + low_principle
            text1 += "\n低賠率為 : " + buy_low_odds 
            message = TextSendMessage(
                text = text1
            )
            line_bot_api.reply_message(event.reply_token,message)
        else:
            low_principle = datalist[0]
            low_odds = datalist[1]
            #計算出高賠率本金
            high_principle = (low_odds - 1) * low_principle
            
            #無條件捨去，因為一注為10元
            b = high_principle % 10
            if int(b) != 9:
                high_principle = high_principle - b
            else:
                high_principle = high_principle - b + 10

            #計算出最低高賠率
            high_odds = (low_principle * low_odds) / high_principle
            buy_high_odds =  decimal.Decimal(high_odds).quantize(decimal.Decimal('0.01'),rounding=decimal.ROUND_UP)
            
            text1 = "現在的模式為高賠率換算低賠率"
            text1 += "\n低賠率本金 : " + low_principle
            text1 += "\n低賠率為 : " + low_odds
            text1 += "\n高賠率本金為 : " + high_principle
            text1 += "\n高賠率為 : " + buy_high_odds 
            message = TextSendMessage(
                text = text1
            )
            line_bot_api.reply_message(event.reply_token,message)
    except:
        text2 = mtext.split( )[0] 
        text2 += "\n請輸入正確格式"
        text2 += "\n如以下範例"
        text2 += "\n本金(空格)賠率"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text2))           

'''
def sendConfirm(event):
    try:
        message = TemplateSendMessage(
            alt_text = '賠率',
            template = ConfirmTemplate(
                text = '請選擇您要計算的賠率',
                actions = [
                    MessageTemplateAction(
                        label = '高賠率',
                        text = '@我要計算高賠率'
                    ),
                    MessageTemplateAction(
                        label = '低賠率',
                        text = '@我要計算低賠率'
                    )
                ]

            ) 
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text = 'Error !'))

#高賠率換算低賠率
def high_calc(event, mode, mtext):
    try:
        #計算出低賠本金
        low_principle = high_principle * (high_odds -1)

        #無條件捨去，因為一注為10元
        b = low_principle % 10
        if int(b) != 9:
            low_principle = low_principle - b
        else:
            low_principle = low_principle - b + 10

        #計算出最少低賠率
        low_odds = high_principle / low_principle + 1
        buy_low_odds =  decimal.Decimal(low_odds).quantize(decimal.Decimal('0.01'),rounding=decimal.ROUND_UP)

        text1 = "現在的模式為高賠率換算低賠率"
        text1 += "\n高賠率本金 : " + high_principle
        text1 += "\n高賠率為 : " + high_odds
        text1 += "\n低賠率本金為 : " + low_principle
        text1 += "\n低賠率為 : " + buy_low_odds 
        message = TextSendMessage(
            text = text1
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        text2 = "請輸入正確格式"
        text2 = "如以下範例"
        text2 += "\n高賠本金(空格)高賠率"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text2))

def low_calc(event, low_principle, low_odds):
    try:
        #計算出高賠率本金
        high_principle = (low_odds - 1) * low_principle
        
        #無條件捨去，因為一注為10元
        b = high_principle % 10
        if int(b) != 9:
            high_principle = high_principle - b
        else:
            high_principle = high_principle - b + 10

        #計算出最低高賠率
        high_odds = (low_principle * low_odds) / high_principle
        buy_high_odds =  decimal.Decimal(high_odds).quantize(decimal.Decimal('0.01'),rounding=decimal.ROUND_UP)
        
        text1 = "現在的模式為高賠率換算低賠率"
        text1 += "\n低賠率本金 : " + low_principle
        text1 += "\n低賠率為 : " + low_odds
        text1 += "\n高賠率本金為 : " + high_principle
        text1 += "\n高賠率為 : " + buy_high_odds 
        message = TextSendMessage(
            text = text1
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        text2 = "請輸入正確格式"
        text2 = "如以下範例"
        text2 += "\n低賠本金(空格)低賠率"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text2))


def track(event):
    try:
        message = TextSendMessage(
            text = '請選擇運輸類別',
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=MessageAction(label = "空運",text = "A")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label = "海運",text = "B")
                    ),

                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '發生錯誤'))

def crawler(trans_type, number):
    r = requests.post(
    'https://portal.sw.nat.gov.tw/APGQ/GB321!query',
    {
    'transType' : trans_type,
    'mawb' : '',
    'hawb' : number,
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
            print('Date : {} time : {} type : {}'.format(data_date,data_time,data_type))
    else:
        print(list_of_dicts['msg'])
'''