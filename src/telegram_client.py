"""Thin wrapper around the Telegram Bot API for posting a photo+caption."""
import os

import requests

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/{method}"


def send_photo(photo_path: str, caption: str) -> dict:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHANNEL_ID"]

    url = TELEGRAM_API_BASE.format(token=token, method="sendPhoto")
    with open(photo_path, "rb") as photo_file:
        response = requests.post(
            url,
            data={"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"},
            files={"photo": photo_file},
            timeout=30,
        )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram API error: {payload}")
    return payload
