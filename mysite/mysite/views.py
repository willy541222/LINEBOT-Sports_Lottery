from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,FlexSendMessage,StickerSendMessage
)

import os,sys,json
import variable_settings as varset
import urllib.parse
from module import func

channel_secret = os.getenv('LINE_CHANNEL_SECRET', 'b7ce414421df207a4f7c49f185e0c5b0')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'A8rE0YCtMEEEr8898I+q25D4JXXD5eGMOc88ANFS7JdxKw5b0yxHN26SNeZRBlv44NWRLkbCjwtmAkeAEeWp8gKnBapOcaCrTyyfwsKEyGzZeFE179ccm8GCqyGeXiCj7K7DflhBwM2+m5icbqiojQdB04t89/1O/w1cDnyilFU=')
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    #sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    #sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

@csrf_exempt
def callback(request):
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.body.decode('utf-8')
    #app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        pass

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        userid, mode = readData(event)
        mtext = event.message.text
        if mtext == '@使用說明':
            func.manual(event)
        #if mtext == '@賠率換算':
        #   func.Togglemode(event, mode, userid)
        elif mtext == '@場中賽況':
            func.game_processing(event)
        elif mtext == '測試':
            func.test(event)
        else :
            func.send_calc(event, mtext)

def readData(event):
    userid = event.source.user_id
    try:
        mode = varset.get(userid)
    except:
        varset.set(userid, 'high')
        mode = 'high'
    return userid, mode
