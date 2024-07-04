from app.models.nutrition import NutritionData
from app.models.flex_message import (
    Text,
    Separator,
    Box,
    Body,
    FooterStyles,
    Styles,
    Bubble,
)
import base64
import mimetypes

from openai import OpenAI
from app import config

from datetime import datetime
from logging import getLogger

logger = getLogger("uvicorn.app")


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
			"calorie": "カロリー(float型)",
			"protein": "タンパク質グラム(float型)",
			"fat": "脂質グラム(float型)",
			"carbohydrate": "炭水化物グラム(float型)"
		}
	],
	"total": {
		"calorie": "合計カロリー(float型)",
		"protein": "合計タンパク質(float型)",
		"fat": "合計脂質(float型)",
		"carbohydrate": "合計炭水化物(float型)"
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


# chatGPTで画像から栄養価を取得する
def get_nutrition_from_image(image_path: str) -> NutritionData:
    base64_image = encode_image(image_path)

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

    return NutritionData.model_validate_json(response.choices[0].message.content)


def create_flex_message(nutrition_data: NutritionData) -> Bubble:
    date_label = Text(
        type="text",
        text=datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        weight="bold",
        size="sm",
        color="#aaaaaa",
    )
    total_calorie_label = Text(
        type="text",
        text="合計カロリー",
        weight="bold",
        size="md",
        color="#3CB371",
    )
    total_calorie = Text(
        type="text",
        text=f"{nutrition_data.total.calorie} kcal",
        weight="bold",
        size="xxl",
        margin="md",
        position="relative",
        align="center",
        color="#1DB446",
    )
    total_pfc = Text(
        type="text",
        text=f"P: {nutrition_data.total.protein}g F: {nutrition_data.total.fat}g C: {nutrition_data.total.carbohydrate}g",
        weight="bold",
        size="sm",
        align="end",
        color="#aaaaaa",
    )
    header_separator = Separator(type="separator")
    food_calorie_details = []
    for food in nutrition_data.food:
        food_name = Text(
            type="text",
            text=f"{food.name}",
            size="sm",
            color="#555555",
            flex=0,
        )
        food_calorie = Text(
            type="text",
            text=f"{food.calorie}kcal",
            size="sm",
            color="#111111",
            align="end",
        )
        food_calorie_detail = Box(
            type="box",
            layout="horizontal",
            contents=[food_name, food_calorie],
        )
        food_calorie_details.append(food_calorie_detail)

    bottom_separator = Separator(type="separator", margin="xxl")
    food_calorie_details.append(bottom_separator)

    food_calories_area = Box(
        type="box",
        layout="vertical",
        margin="xxl",
        spacing="sm",
        contents=food_calorie_details,
    )

    body = Body(
        type="box",
        layout="vertical",
        contents=[
            date_label,
            total_calorie_label,
            total_calorie,
            total_pfc,
            header_separator,
            food_calories_area,
        ],
    )
    footer = Styles(footer=FooterStyles(separator=True))
    bubble = Bubble(type="bubble", body=body, styles=footer)
    logger.info(bubble.model_dump_json(exclude_none=True))
    return bubble
