import os
import time
from pathlib import Path

import edge_tts

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


# =========================
# VOICES
# =========================

VOICES = {

    # فارسی
    "fa_farid": {
        "language": "fa",
        "name": "🇮🇷 فارسی - Farid",
        "voice": "fa-IR-FaridNeural",
    },

    # هلندی
    "nl_maarten": {
        "language": "nl",
        "name": "🇳🇱 Nederlands - Maarten",
        "voice": "nl-NL-MaartenNeural",
    },

    "nl_colette": {
        "language": "nl",
        "name": "🇳🇱 Nederlands - Colette",
        "voice": "nl-NL-ColetteNeural",
    },

    # انگلیسی
    "en_guy": {
        "language": "en",
        "name": "🇬🇧 English - Guy",
        "voice": "en-US-GuyNeural",
    },

    "en_jenny": {
        "language": "en",
        "name": "🇺🇸 English - Jenny",
        "voice": "en-US-JennyNeural",
    },
}


# =========================
# DEFAULT SETTINGS
# =========================

DEFAULT_VOICE = "fa_farid"
DEFAULT_SPEED = 0


# =========================
# SPEED
# =========================

SPEEDS = {
    -1: "🐢 یک درجه کمتر",
    0: "🎙️ سرعت معمولی",
    1: "⚡ یک درجه بیشتر",
}


def get_rate(speed):

    if speed == -1:
        return "-15%"

    if speed == 1:
        return "+15%"

    return "+0%"


# =========================
# PERMANENT MENU
# =========================

def main_menu():

    keyboard = [

        ["🇮🇷 فارسی"],

        ["🇳
