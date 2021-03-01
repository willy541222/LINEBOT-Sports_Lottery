from django.conf import settings

from linebot import LineBotApi, WebhookParser
from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction,StickerSendMessage, TemplateSendMessage, ConfirmTemplate, MessageTemplateAction, PostbackTemplateAction, FlexSendMessage
import os, json, requests
from datetime import datetime, timedelta, timezone
import random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pandas as pd
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

#使用說明
def manual(event):
    try:
        text0 = "使用說明如下"
        message = TextSendMessage(
            text = text0
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        message0 = [
            StickerSendMessage(
                package_id='2',
                sticker_id='161'
            ),

            TextSendMessage(
                text = "工程師正在修復中"
            )
        ]
        line_bot_api.reply_message(event.reply_token, message0)

#計算本金賠率
def send_calc(event, mtext):
    try:
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

        #mode_name = "模式為高賠率換算低賠率"
        total_principle = "$ " +  str(high_principle + low_principle)
        high_principle ="$ " + str(high_principle)
        high_odds = str(high_odds)
        low_principle ="$ " + str(low_principle)
        buy_low_odds = str(buy_low_odds)
        message = FlexSendMessage(
            alt_text = "賠率計算器",
            contents = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": "賠率計算機",
                        "weight": "bold",
                        "size": "xl",
                        "margin": "md",
                        "color": "#1DB446",
                        "align": "start"
                    },
                    {
                        "type": "text",
                        "text": "下注賠率時計算最低賠率多少能對沖",
                        "size": "xs",
                        "margin": "md",
                        "color": "#aaaaaa",
                        "wrap": True
                    },
                    {
                        "type": "separator",
                        "margin": "xxl"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "xxl",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                            {
                                "type": "text",
                                "text": "下注本金",
                                "size": "sm",
                                "color": "#555555",
                                "flex": 0
                            },
                            {
                                "type": "text",
                                "text": high_principle,
                                "size": "sm",
                                "color": "#111111",
                                "align": "end"
                            }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                            {
                                "type": "text",
                                "text": "下注賠率",
                                "size": "sm",
                                "color": "#555555",
                                "flex": 0
                            },
                            {
                                "type": "text",
                                "text": high_odds,
                                "size": "sm",
                                "color": "#111111",
                                "align": "end"
                            }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                            {
                                "type": "text",
                                "text": "最多能下注的本金",
                                "size": "sm",
                                "color": "#555555"
                            },
                            {
                                "type": "text",
                                "text": low_principle,
                                "size": "sm",
                                "color": "#FF0000",
                                "align": "end"
                            }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                            {
                                "type": "text",
                                "text": "最低下注賠率",
                                "size": "sm",
                                "color": "#555555"
                            },
                            {
                                "type": "text",
                                "text": buy_low_odds,
                                "size": "sm",
                                "color": "#FF0000",
                                "align": "end"
                            }
                            ]
                        }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "xxl"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": [
                        {
                            "type": "text",
                            "text": "下注總金額",
                            "size": "xs",
                            "color": "#aaaaaa",
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": total_principle,
                            "color": "#aaaaaa",
                            "size": "xs",
                            "align": "end"
                        }
                        ]
                    }
                    ]
                },
                "styles": {
                    "footer": {
                    "separator": True
                    }
                }
            }
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
        res = requests.get("https://blob.sportslottery.com.tw/apidata/Live/On.json", headers = headers)
        #print(res.status_code) #顯示網頁回傳狀態
        data = res.json()

        if len(data) == 0:
            text4 = "目前沒有任何賽事"
            message = TextSendMessage(
                text = text4
            )
            line_bot_api.reply_message(event.reply_token,message)
        else:
            message =[]
            for i in range(len(data)):
                Game_name = data[i]['ln'][0] #比賽名稱
                player_one_chinese = data[i]['atn'][0] #中文名字
                #player_one_english = data[i]['atn'][1] #英文名字
                player_two_chinese = data[i]['htn'][0] #中文名字
                #player_two_english = data[i]['htn'][1] #英文名字
                player_one_score = data[i]['as'].get('10') #當局分數 ex:tennis 
                player_two_score = data[i]['hs'].get('10') #當局分數 ex:tennis

                text3 = Game_name  + "\n"
                text3 += player_one_chinese + " : " + player_two_chinese + "\n"
                for b in range(len(data[i]['as'])):
                    b = b + 1
                    player_one_as = data[i]['as'].get(str(b)) #分數
                    if player_one_as == -1 :
                        break
                    else:
                        player_two_hs = data[i]['hs'].get(str(b)) #分數
                        text3 += "第"+ str(b) +"局" + str(player_one_as) + " : " + str(player_two_hs) + "\n"
                
                #if player_one_score != -1:
                if data[i]['si'] == 445: #網球
                    text3 += "當盤分數" + str(player_one_score) + " : " + str(player_two_score) + "\n" #當局分數
                
                if data[i]['si'] == 441: #足球
                    text3 += "目前進行時間 : " + data[i]['ed'][21:23] + " 分鐘\n" #目前進行時間

                res1 = requests.get("https://h2h.sportslottery.com.tw/sportradar/zht/h2h.html?matchID={}".format(data[i]['mi']), headers = headers)
                if res1.status_code == 200 :
                    text3 += "場中動畫連結\n"
                    text3 += "https://h2h.sportslottery.com.tw/sportradar/zht/h2h.html?matchID=" + str(data[i]['mi']) + "\n"
                message0 = TextSendMessage(
                    text=text3
                )
                message.append(message0)
            line_bot_api.reply_message(event.reply_token,message)
    except:
        message1 = [
            StickerSendMessage(
                package_id='2',
                sticker_id='161'
            ),

            TextSendMessage(
                text = "工程師正在修復中"
            )
        ]
        line_bot_api.reply_message(event.reply_token, message1)

def test(event):
    try:
        message = []
        ua = UserAgent()
        user_agent = ua.random
        headers = {'user-agent': user_agent}
        res = requests.get("https://blob.sportslottery.com.tw/apidata/Live/On.json", headers = headers)
        #print(res.status_code) #顯示網頁回傳狀態
        data = res.json()
        if len(data) == 0:
            count = 0
            message = [TextSendMessage(text = "目前無任何比賽，以下是即將開始的單場暨場中")]
            ub = UserAgent()
            user_agent = ub.random
            headers = {'user-agent': user_agent}
            url = "https://www.sportslottery.com.tw/zh-tw/news/live-schedule"
            res1 = requests.get(url, headers = headers)
            #msg = res1.status_code
            df = pd.read_html(res1.text)[0]
            now = datetime.utcnow().replace(tzinfo=timezone.utc)
            tw_time = now.astimezone(timezone(timedelta(hours=8)))
            now_time = tw_time.strftime("%Y-%m-%d")
            for i in range(len(df.index)):
                df1 = df.iloc[i][0].split('/')
                df_year = str(int(df1[0]) + 1911)
                df_time = df_year + '-' + df1[1] +'-'+ df1[2]
                time_cond = int(df.iloc[i][2][:2])-int(tw_time.strftime("%H"))
                if df_time == now_time and df.iloc[i][-1] == '單場+場中' and time_cond>0:
                    count += 1
                    #print(df.iloc[i][1::])
                    game_name = df.iloc[i][3]
                    away_team = df.iloc[i][4]
                    home_team = df.iloc[i][5]
                    #team = str(df.iloc[i][4]) + ' vs ' + str(df.iloc[i][5])
                    game_time = str(df.iloc[i][2])
                    message1 = FlexSendMessage(
                        alt_text="Schedule",
                        contents={
                            "type": "bubble",
                            "body": {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": game_name,
                                    "weight": "bold",
                                    "size": "xxl",
                                    "margin": "md"
                                },
                                {
                                    "type": "separator",
                                    "margin": "xxl"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "margin": "xxl",
                                    "spacing": "sm",
                                    "contents": [
                                    {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "時間",
                                            "size": "sm",
                                            "color": "#555555",
                                            "flex": 0
                                        },
                                        {
                                            "type": "text",
                                            "text": game_time,
                                            "size": "sm",
                                            "align": "center"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "主隊",
                                            "size": "sm",
                                            "color": "#555555",
                                            "flex": 0
                                        },
                                        {
                                            "type": "text",
                                            "text": away_team,
                                            "size": "sm",
                                            "color": "#006D77",
                                            "align": "center"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "客隊",
                                            "size": "sm",
                                            "color": "#555555",
                                            "flex": 0
                                        },
                                        {
                                            "type": "text",
                                            "text": home_team,
                                            "size": "sm",
                                            "color": "#006D77",
                                            "align": "center"
                                        }
                                        ]
                                    }
                                    ]
                                },
                                {
                                    "type": "separator",
                                    "margin": "xxl"
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "margin": "md",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": "單場＋場中投注",
                                        "size": "xs",
                                        "color": "#aaaaaa",
                                        "flex": 0
                                        }
                                    ]
                                }
                                ]
                            },
                            "styles": {
                                "footer": {
                                "separator": True
                                }
                            }
                        }
                    )
                    message.append(message1)
                    if count == 4:
                        break
            if message1 == None:
                message = TextSendMessage(
                    text = "今天沒有任何比賽了"
                )
            line_bot_api.reply_message(event.reply_token, message)
        else:
            message =[]
            for i in range(len(data)):
                Game_name = data[i]['ln'][0] #比賽名稱
                player_one_chinese = data[i]['atn'][0] #中文名字
                player_one_english = data[i]['atn'][1] #英文名字
                player_two_chinese = data[i]['htn'][0] #中文名字
                player_two_english = data[i]['htn'][1] #英文名字
                player_one_score = data[i]['as'].get('10') #當局分數 ex:tennis 
                player_two_score = data[i]['hs'].get('10') #當局分數 ex:tennis

                text3 = Game_name  + "\n"
                text3 += player_one_chinese + " : " + player_two_chinese + "\n"
                for b in range(len(data[i]['as'])):
                    b = b + 1
                    player_one_as = data[i]['as'].get(str(b)) #分數
                    if player_one_as == -1 :
                        break
                    else:
                        player_two_hs = data[i]['hs'].get(str(b)) #分數
                        text3 += "第"+ str(b) +"局" + str(player_one_as) + " : " + str(player_two_hs) + "\n"

                if data[i]['si'] == 443: #棒球
                    Team_name = player_one_chinese + " vs " + player_two_chinese
                    Team_name_en = player_one_english + " vs " + player_two_english
                    Game_one_score = str(data[i]['as'].get('1')) + " : " + str(data[i]['hs'].get('1'))
                    total_score = 0
                    Game_score = []
                    for a in range(len(data[i]['as'])):
                        if data[i]['as'].get(str(a)) == -1:
                            Game_score[a+1] = " "
                            Game_score[a+1] = str(Game_score[a+1])
                        else:
                            Game_score[a+1] = str(data[i]['as'].get(str(a))) + " : " + str(data[i]['hs'].get(str(a)))
                            Game_score[a+1] = str(Game_score[a+1])
                            total_score = total_score + data[i]['as'].get(str(a)) + data[i]['hs'].get(str(a))
                            total_score = str(total_score)
                    message0 = FlexSendMessage(
                        alt_text = "Baseball",
                        contents = {
                            "type": "bubble",
                            "body": {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": Game_name,
                                    "weight": "bold",
                                    "color": "#1DB446",
                                    "size": "sm"
                                },
                                {
                                    "type": "text",
                                    "text": Team_name,
                                    "weight": "bold",
                                    "size": "xxl",
                                    "margin": "none",
                                    "align": "start"
                                },
                                {
                                    "type": "text",
                                    "text": Team_name_en,
                                    "size": "xs",
                                    "color": "#aaaaaa",
                                    "wrap": True
                                },
                                {
                                    "type": "separator",
                                    "margin": "xxl"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "margin": "xxl",
                                    "spacing": "sm",
                                    "contents": [
                                    {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "第一局",
                                            "size": "sm",
                                            "color": "#555555",
                                            "flex": 0
                                        },
                                        {
                                            "type": "text",
                                            "text": Game_score[1],
                                            "size": "sm",
                                            "color": "#111111",
                                            "align": "center",
                                            "weight": "bold"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "第二局",
                                            "size": "sm",
                                            "color": "#555555",
                                            "flex": 0
                                        },
                                        {
                                            "type": "text",
                                            "size": "sm",
                                            "color": "#111111",
                                            "align": "center",
                                            "text": Game_score[2],
                                            "weight": "bold"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "第三局",
                                            "size": "sm",
                                            "color": "#555555",
                                            "flex": 0
                                        },
                                        {
                                            "type": "text",
                                            "text": Game_score[3],
                                            "size": "sm",
                                            "color": "#111111",
                                            "align": "center",
                                            "weight": "bold"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "第四局",
                                            "size": "sm",
                                            "color": "#555555",
                                            "flex": 0
                                        },
                                        {
                                            "type": "text",
                                            "text":Game_score[4],
                                            "size": "sm",
                                            "color": "#111111",
                                            "align": "center",
                                            "weight": "bold"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "第五局",
                                            "size": "sm",
                                            "color": "#555555",
                                            "flex": 0
                                        },
                                        {
                                            "type": "text",
                                            "text": Game_score[5],
                                            "size": "sm",
                                            "color": "#111111",
                                            "align": "center",
                                            "weight": "bold"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "第六局",
                                            "size": "sm",
                                            "color": "#555555",
                                            "flex": 0
                                        },
                                        {
                                            "type": "text",
                                            "text": Game_score[6],
                                            "size": "sm",
                                            "color": "#111111",
                                            "align": "center",
                                            "weight": "bold"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "第七局",
                                            "size": "sm",
                                            "color": "#555555",
                                            "flex": 0
                                        },
                                        {
                                            "type": "text",
                                            "text": Game_score[7],
                                            "size": "sm",
                                            "color": "#111111",
                                            "align": "center",
                                            "weight": "bold"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "第八局",
                                            "size": "sm",
                                            "flex": 0,
                                            "color": "#555555"
                                        },
                                        {
                                            "type": "text",
                                            "text": Game_score[8],
                                            "weight": "bold",
                                            "align": "center",
                                            "color": "#111111",
                                            "size": "sm"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "第九局",
                                            "flex": 0,
                                            "size": "sm",
                                            "color": "#555555"
                                        },
                                        {
                                            "type": "text",
                                            "text":Game_score[9],
                                            "size": "sm",
                                            "color": "#111111",
                                            "weight": "bold",
                                            "align": "center"
                                        }
                                        ]
                                    },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                        "type": "text",
                                        "text": "延長",
                                        "flex": 0,
                                        "size": "sm",
                                        "color": "#555555"
                                        },
                                        {
                                        "type": "text",
                                        "text": Game_score[10],
                                        "size": "sm",
                                        "color": "#111111",
                                        "weight": "bold",
                                        "align": "center"
                                        }
                                    ]
                                    }
                                    ]
                                },
                                {
                                    "type": "separator",
                                    "margin": "xxl"
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "margin": "md",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": "總分",
                                        "size": "lg",
                                        "color": "#aaaaaa",
                                        "flex": 0
                                    },
                                    {
                                        "type": "text",
                                        "text": total_score,
                                        "color": "#0066CC",
                                        "size": "lg",
                                        "align": "center",
                                        "weight": "bold"
                                    }
                                    ]
                                }
                                ]
                            },
                            "styles": {
                                "footer": {
                                "separator": True
                                }
                            }
                        }
                    )
                
                if data[i]['si'] == 445: #網球
                    au_score = str(player_one_score) + " : " + str(player_two_score) #當局分數
                    Team_name = player_one_chinese + " vs " + player_two_chinese
                    Game_one_score = str(data[i]['as'].get('1')) + " : " + str(data[i]['hs'].get('1'))
                    Game_animation_url = "https://h2h.sportslottery.com.tw/sportradar/zht/h2h.html?matchID=" + str(data[i]['mi'])
                    if data[i]['as'].get('2') == -1:
                        Game_two_score = " "
                    else:
                        Game_two_score = str(data[i]['as'].get('2')) + " : " + str(data[i]['hs'].get('2'))                                    
                    if data[i]['as'].get('3') == -1:
                        Game_three_score = " "
                    else:
                        Game_three_score = str(data[i]['as'].get('3')) + " : " + str(data[i]['hs'].get('3'))
                    message0 = FlexSendMessage(
                        alt_text= "Tennis",
                        contents= {
                            "type": "bubble",
                            "body": {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": Game_name,
                                    "weight": "bold",
                                    "size": "xs",
                                    "color": "#999999",
                                    "align": "start"
                                },
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "margin": "md",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "size": "md",
                                        "margin": "none",
                                        "flex": 0,
                                        "weight": "bold",
                                        "text": Team_name
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
                                            "text": Game_one_score,
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
                                            "text": Game_two_score,
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
                                            "text": "第三局",
                                            "flex": 1,
                                            "size": "xs",
                                            "color": "#aaaaaa"
                                        },
                                        {
                                            "type": "text",
                                            "text": Game_three_score,
                                            "flex": 5,
                                            "size": "sm",
                                            "color": "#666666",
                                            "align": "center",
                                            "weight": "bold",
                                            "wrap": True
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "當局分數",
                                            "size": "xs"
                                        },
                                        {
                                            "type": "text",
                                            "text": au_score,
                                            "size": "sm",
                                            "weight":"bold"
                                        }
                                        ]
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
                                    "uri": Game_animation_url
                                    },
                                    "color": "#905c44"
                                }
                                ],
                                "flex": 0
                            }
                        }
                    )

                if data[i]['si'] == 441: #足球
                    Game_animation_url = "https://h2h.sportslottery.com.tw/sportradar/zht/h2h.html?matchID=" + str(data[i]['mi'])
                    Game_time = "目前進行時間 : " + data[i]['ed'][21:23] + " 分鐘" #目前進行時間
                    Team_name = player_one_chinese + " vs " + player_two_chinese
                    Game_one_score = str(data[i]['as'].get('1')) + " : " + str(data[i]['hs'].get('1'))
                    if data[i]['as'].get('2') == -1:
                        Game_two_score = " "
                    else:
                        Game_two_score = str(data[i]['as'].get('2')) + " : " + str(data[i]['hs'].get('2'))
                    message0 = FlexSendMessage(
                        alt_text= "Soccer",
                        contents = {
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
                                    "align": "start"
                                },
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "margin": "md",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": Team_name,
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
                                            "text": Game_one_score,
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
                                            "text": Game_two_score,
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
                                            "text": Game_time,
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
                                    "uri": Game_animation_url
                                    },
                                    "color": "#905c44"
                                }
                                ],
                                "flex": 0
                                }
                            }
                    )
                message.append(message0)
            line_bot_api.reply_message(event.reply_token,message)
    except:
        message1 = [
            StickerSendMessage(
                package_id='2',
                sticker_id='161'
            ),

            TextSendMessage(
                text = "工程師正在修復中"
            )
        ]
        line_bot_api.reply_message(event.reply_token, message1)


'''
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