from django.conf import settings

from linebot import LineBotApi, WebhookParser
from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction,StickerSendMessage, TemplateSendMessage, ConfirmTemplate, MessageTemplateAction, PostbackTemplateAction, FlexSendMessage
import os, json, requests
import random
from fake_useragent import UserAgent
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
    try:
        if mode == 'high':
            high_principle = int(mtext.split('/')[0]) 
            high_odds = float(mtext.split('/')[1]) 
            #計算出低賠本金
            low_principle = high_principle * (high_odds -1)
            low_principle = int(low_principle)

            #無條件捨去，因為一注為10元
            b = low_principle % 10
            if int(b) != 9:
                low_principle = low_principle - b
            else:
                low_principle = low_principle - b + 10

            #計算出最少低賠率
            low_odds = high_principle / low_principle + 1
            buy_low_odds =  decimal.Decimal(low_odds).quantize(decimal.Decimal('0.01'),rounding=decimal.ROUND_UP)

            text1 = "模式為高賠率換算低賠率"
            text1 += "\n高賠率本金 : " + str(high_principle) + "元"
            text1 += "\n高賠率為 : " + str(high_odds)
            text1 += "\n低賠率本金為 : " + str(low_principle) + "元"
            text1 += "\n低賠率為 : " + str(buy_low_odds) 
            message = TextSendMessage(
                text = text1
            )
            line_bot_api.reply_message(event.reply_token,message)
        else:
            low_principle = int(mtext.split('/')[0])
            low_odds = float(mtext.split('/')[1])
            #計算出高賠率本金
            high_principle = (low_odds - 1) * low_principle
            high_principle = int(high_principle)
            #無條件捨去，因為一注為10元
            b = high_principle % 10

            if int(b) != 9:
                high_principle = high_principle - b
            else:
                high_principle = high_principle - b + 10

            #計算出最低高賠率
            high_odds = (low_principle * low_odds) / high_principle
            buy_high_odds =  decimal.Decimal(high_odds).quantize(decimal.Decimal('0.01'),rounding=decimal.ROUND_UP)
            
            text1 = "模式為低賠率換算高賠率"
            text1 += "\n低賠率本金 : " + str(low_principle) + "元"
            text1 += "\n低賠率為 : " + str(low_odds)
            text1 += "\n高賠率本金為 : " + str(high_principle) + "元"
            text1 += "\n高賠率為 : " + str(buy_high_odds) 
            message = TextSendMessage(
                text = text1
            )
            line_bot_api.reply_message(event.reply_token,message)
    except:
        #輸入錯誤則顯示正確格式範例
        text2 = "請輸入正確格式"
        text2 += "\n如以下範例"
        text2 += "\n本金/賠率"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text2))           

#場中賽況
def game_processing(event):
    try:
        ua = UserAgent()
        user_agent = ua.random
        headers = {'user-agent': user_agent}
        res = requests.get("https://www.sportslottery.com.tw/api/services/app/LiveGames/GetLiveOnAndRegister?isContainRegister=false", headers = headers)
        #print(res.status_code) #顯示網頁回傳狀態
        data = res.json()
        Game_data = data['result']['liveOn']

        if len(Game_data) == 0:
            text4 = "目前沒有任何賽事"
            message = TextSendMessage(
                text = text4
            )
            line_bot_api.reply_message(event.reply_token,message)
        else:
            text3 = "目前場中投注的賽事\n"
            for i in range(len(Game_data)):
                Game_name = Game_data[i]['ln'][0] #比賽名稱
                player_one_chinese = Game_data[i]['atn'][0] #中文名字
                #player_one_english = Game_data[i]['atn'][1] #英文名字
                player_two_chinese = Game_data[i]['htn'][0] #中文名字
                #player_two_english = Game_data[i]['htn'][1] #英文名字
                player_one_score = Game_data[i]['as'].get('10') #當局分數 ex:tennis 
                player_two_score = Game_data[i]['hs'].get('10') #當局分數 ex:tennis

                text3 += Game_name  + "\n"
                text3 += player_one_chinese + " : " + player_two_chinese + "\n"
                for b in range(len(Game_data[i]['as'])):
                    b = b + 1
                    player_one_as = Game_data[i]['as'].get(str(b)) #分數
                    if player_one_as == -1 :
                        break
                    else:
                        player_two_hs = Game_data[i]['hs'].get(str(b)) #分數
                        text3 += "第"+ str(b) +"局" + str(player_one_as) + " : " + str(player_two_hs) + "\n"
                
                #if player_one_score != -1:
                if Game_data[i]['si'] == 445: #網球
                    text3 += "當盤分數" + str(player_one_score) + " : " + str(player_two_score) + "\n" #當局分數
                
                if Game_data[i]['si'] == 441: #足球
                    text3 += "目前進行時間 : " + Game_data[i]['ed'][21:23] + " 分鐘\n" #目前進行時間

                res1 = requests.get("https://h2h.sportslottery.com.tw/sportradar/zht/h2h.html?matchID={}".format(Game_data[i]['mi']), headers = headers)
                if res1.status_code == 200 :
                    text3 += "場中動畫連結\n"
                    text3 += "https://h2h.sportslottery.com.tw/sportradar/zht/h2h.html?matchID=" + str(Game_data[i]['mi']) + "\n"
                    
            message = TextSendMessage(
                text = text3
            )
            line_bot_api.reply_message(event.reply_token,message)
    except:
        message1 = [
            StickerSendMessage(
                package_id='1',
                sticker_id='105'
            ),

            TextSendMessage(
                text = "工程師正在修復中"
            )
        ]
        line_bot_api.reply_message(event.reply_token, message1)

def test(event):
    try:
        ua = UserAgent()
        user_agent = ua.random
        headers = {'user-agent': user_agent}
        res = requests.get("https://www.sportslottery.com.tw/api/services/app/LiveGames/GetLiveOnAndRegister?isContainRegister=false", headers = headers)
        #print(res.status_code) #顯示網頁回傳狀態
        data = res.json()
        Game_data = data['result']['liveOn']
        
        if len(Game_data) == 0:
            text4 = "目前沒有任何賽事"
            message = TextSendMessage(
                text = text4
            )
            line_bot_api.reply_message(event.reply_token,message)
        else:
            text3 = TextSendMessage(
                text = "目前場中投注的賽事"
            ) 
            for i in range(len(Game_data)):
                Game_name = Game_data[i]['ln'][0] #比賽名稱
                player_one_chinese = Game_data[i]['atn'][0] #中文名字
                player_two_chinese = Game_data[i]['htn'][0] #中文名字
                player_one_as_1 = Game_data[i]['as'].get('1') #Game one score
                player_two_hs_1 = Game_data[i]['hs'].get('1') #Game one score
                player_one_as_2 = Game_data[i]['as'].get('2') #Game one score
                player_two_hs_2 = Game_data[i]['hs'].get('2') #Game one score
                game_time= "目前進行時間 : " + Game_data[i]['ed'][21:23] + " 分鐘" #目前進行時間
                game_one_score = str(player_one_as_1) + " : " + str(player_two_hs_1)
                res1 = requests.get("https://h2h.sportslottery.com.tw/sportradar/zht/h2h.html?matchID={}".format(Game_data[i]['mi']), headers = headers)
                if res1.status_code == 200 :
                    game_video = "https://h2h.sportslottery.com.tw/sportradar/zht/h2h.html?matchID=" + str(Game_data[i]['mi']) + "\n"
                if player_one_as_2 == -1:
                    game_two_score = " "
                else:
                    game_two_score = str(player_one_as_2) + " : " + str(player_two_hs_2)
                message1 = FlexSendMessage(
                            alt_text="足球場中賽況",
                            contents={
                                "type": "bubble",
                                "body": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": Game_name,
                                        "weight": "bold",
                                        "size": "sm",
                                        "color": "#999999",
                                    },
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "margin": "md",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": player_one_chinese + "VS" + player_two_chinese,
                                            "size": "md",
                                            "margin": "none",
                                            "flex": 0,
                                            "weight": "bold"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "margin": "lg",
                                        "spacing": "sm",
                                        "contents": [
                                        {
                                            "type": "box",
                                            "layout": "baseline",
                                            "spacing": "sm",
                                            "contents": [
                                            {
                                                "type": "text",
                                                "text": "第一局",
                                                "color": "#aaaaaa",
                                                "size": "xs",
                                                "flex": 1
                                            },
                                            {
                                                "type": "text",
                                                "text": game_one_score,
                                                "wrap": True,
                                                "color": "#666666",
                                                "size": "sm",
                                                "flex": 5,
                                                "align": "center",
                                                "weight": "bold"
                                            }
                                            ]
                                        },
                                        {
                                            "type": "box",
                                            "layout": "baseline",
                                            "spacing": "sm",
                                            "contents": [
                                            {
                                                "type": "text",
                                                "text": "第二局",
                                                "color": "#aaaaaa",
                                                "size": "xs",
                                                "flex": 1
                                            },
                                            {
                                                "type": "text",
                                                "text": game_two_score,
                                                "wrap": True,
                                                "color": "#666666",
                                                "size": "sm",
                                                "flex": 5,
                                                "align": "center",
                                                "weight": "bold"
                                            }
                                            ]
                                        },
                                        {
                                            "type": "box",
                                            "layout": "baseline",
                                            "contents": [
                                            {
                                                "type": "text",
                                                "text": game_time,
                                                "margin": "none",
                                                "size": "xs",
                                                "weight": "bold"
                                            }
                                            ],
                                            "spacing": "none",
                                            "margin": "md"
                                        }
                                        ]
                                    }
                                    ]
                                },
                                "footer": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "spacing": "sm",
                                    "contents": [
                                    {
                                        "type": "spacer"
                                    },
                                    {
                                        "type": "button",
                                        "style": "primary",
                                        "height": "sm",
                                        "action": {
                                        "type": "uri",
                                        "label": "動畫直播",
                                        "uri": game_video
                                        },
                                        "color": "#905c44"
                                    }
                                    ],
                                    "flex": 0
                                }
                            }
                        )
                message = [text3, message1]
                line_bot_api.reply_message(event.reply_token,message)
    except:
        message =StickerSendMessage(
                package_id='1',
                sticker_id='105'
            )
        line_bot_api.reply_message(event.reply_token, message)



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