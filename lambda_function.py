import os
import sys
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, MessageAction,
    TemplateSendMessage, ButtonsTemplate
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
import logging
import datetime

DIFF_JST_FROM_UTC = 9
dt_now = datetime.datetime.now() + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
dt_hour_now = str(dt_now.hour)
dt_minute_now = str(dt_now.minute)

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    logger.error('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    logger.error('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


def lambda_handler(event, context):
    ok_json = {"isBase64Encoded": False,
               "statusCode": 200,
               "headers": {},
               "body": ""}
    error_json = {"isBase64Encoded": False,
                  "statusCode": 403,
                  "headers": {},
                  "body": "Error"}

    signature = event["headers"]["X-Line-Signature"]
    body = event['body']

    @handler.add(MessageEvent, message=TextMessage)
    def message(line_event):
        text = line_event.message.text
        if text == "こんにちは":
            line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text="こんにちはですぅ～"))
        elif text == "こんばんは":
            line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text="夜の帳が落ちましたか…"))
        elif text == "おはよう":
            line_bot_api.reply_message(line_event.reply_token,
                                       TextSendMessage(text="こんな時間におはようだなんて…\n気が抜けてるんじゃないですか！？"))
        elif text == "時間":
            line_bot_api.reply_message(line_event.reply_token,
                                       TextSendMessage(text="私が" + dt_hour_now + "時" + dt_minute_now + "分をお送りいたしました。"))

        elif text == "Myprofile":
            profile = line_bot_api.get_profile(line_event.source.user_id)
            status_msg = profile.status_message
            if status_msg is None:
                status_msg = "なし"

            messages = TemplateSendMessage(alt_text="Buttons template",
                                           template=ButtonsTemplate(
                                               thumbnail_image_url=profile.picture_url,
                                               title=profile.display_name,
                                               text=f"User Id: {profile.user_id[:5]}...\n"
                                                    f"Status Message: {status_msg}",
                                               actions=[MessageAction(label='成功', text="押しちゃった！")]))

            line_bot_api.reply_message(line_event.reply_token, messages=messages)

        elif text == "押しちゃった！":
            line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text="押しちゃったねぇ～"))
        else:
            line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text=text))

    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        logger.error("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            logger.error(" %s: %s" % (m.property, m.message))
        return error_json
    except InvalidSignatureError:
        return error_json

    return ok_json