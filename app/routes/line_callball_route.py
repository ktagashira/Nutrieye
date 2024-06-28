from fastapi import APIRouter, BackgroundTasks, Header, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage
from starlette.exceptions import HTTPException
from openai import OpenAI

from app import config

import base64
import mimetypes

line_bot_callback_router = APIRouter(prefix="", tags=["line_bot"])
line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)

openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
MODEL = "gpt-4o"
SYSTEM_PROMPT = (
    "あなたは栄養管理をするAIです。聞かれたことに対して、JSON形式で回答します。"
)
USER_MESSAGE = """
写真に写っている食べ物と、それぞれのカロリーとPFCバランスを教えてください。
出力形式
食べ物が写っていた場合
{
	"food": [
		{
			"name": "食べ物名",
			"calorie": "カロリー(kcal)",
			"protein": "タンパク質(g)",
			"fat": "脂質(g)",
			"carbohydrate": "炭水化物(g)"
		}
	],
	"total": {
		"calorie": "合計カロリー(kcal)",
		"protein": "合計タンパク質(g)",
		"fat": "合計脂質(g)",
		"carbohydrate": "合計炭水化物(g)"
	}
}
食べ物が写っていなかった場合
{"error": "食べ物が写っていません"}
"""


def encode_image(image_path: str):
    """Encodes an image to base64 and determines the correct MIME type."""
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        raise ValueError(f"Cannot determine MIME type for {image_path}")

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded_string}"


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

    base64_image = encode_image(image_file_path)

    response = openai_client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": USER_MESSAGE,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": base64_image,
                            "detail": "high",
                        },
                    },
                ],
            },
        ],
    )

    message = TextMessage(text=response.choices[0].message.content)
    line_bot_api.reply_message(event.reply_token, message)
