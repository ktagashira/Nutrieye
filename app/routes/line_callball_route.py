from fastapi import APIRouter, BackgroundTasks, Header, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, FlexSendMessage
from starlette.exceptions import HTTPException
from pydantic import ValidationError

from app import config
from app.utils.utils import get_nutrition_from_image, create_flex_message


line_bot_callback_router = APIRouter(prefix="", tags=["line_bot"])
line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)


@line_bot_callback_router.post("/callback")
async def callback(
    request: Request,
    background_tasks: BackgroundTasks,
    x_line_signature=Header(None),
):
    """Line Bot用のエンドポイント"""
    body = await request.body()

    try:
        background_tasks.add_task(
            handler.handle, body.decode("utf-8"), x_line_signature
        )
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "ok"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_massage(event):
    image_file_path = "/tmp/file.png"
    message_content = line_bot_api.get_message_content(event.message.id)

    with open(image_file_path, "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)
    try:
        nutrition_data = get_nutrition_from_image(image_file_path)
    except ValidationError:
        message = TextMessage(text="食べ物が写っていません")
        line_bot_api.reply_message(event.reply_token, message)
        return

    flex_babble = create_flex_message(nutrition_data)
    payload = flex_babble.model_dump(exclude_none=True)
    message = FlexSendMessage(alt_text="栄養価を算出しました", contents=payload)
    line_bot_api.reply_message(event.reply_token, message)
