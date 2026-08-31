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

        ["🇳🇱 صدای هلندی", "🇬🇧 صدای انگلیسی"],

        ["🎙️ انتخاب صدای هلندی",
         "🎙️ انتخاب صدای انگلیسی"],

        ["🐢 سرعت کمتر",
         "🎙️ سرعت معمولی",
         "⚡ سرعت بیشتر"],

    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["voice"] = DEFAULT_VOICE
    context.user_data["speed"] = DEFAULT_SPEED

    await update.message.reply_text(

        "🎙️ Ali Voice Pro\n\n"
        "ربات آماده است.\n"
        "زبان و صدا را از دکمه‌های پایین انتخاب کن.\n\n"
        "🇮🇷 فارسی\n"
        "🇳🇱 Nederlands\n"
        "🇬🇧 English",

        reply_markup=main_menu()
    )


# =========================
# INLINE VOICE MENU
# =========================

async def show_dutch_voices(update, context):

    buttons = [

        [
            InlineKeyboardButton(
                "🇳🇱 Maarten",
                callback_data="voice_nl_maarten"
            )
        ],

        [
            InlineKeyboardButton(
                "🇳🇱 Colette",
                callback_data="voice_nl_colette"
            )
        ],

    ]

    await update.message.reply_text(
        "🎙️ صدای هلندی را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def show_english_voices(update, context):

    buttons = [

        [
            InlineKeyboardButton(
                "🇬🇧 Guy",
                callback_data="voice_en_guy"
            )
        ],

        [
            InlineKeyboardButton(
                "🇺🇸 Jenny",
                callback_data="voice_en_jenny"
            )
        ],

    ]

    await update.message.reply_text(
        "🎙️ صدای انگلیسی را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# =========================
# BUTTON HANDLER
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    mapping = {

        "voice_nl_maarten":
            "nl_maarten",

        "voice_nl_colette":
            "nl_colette",

        "voice_en_guy":
            "en_guy",

        "voice_en_jenny":
            "en_jenny",

    }

    if data in mapping:

        selected = mapping[data]

        context.user_data["voice"] = selected

        await query.edit_message_text(

            "✅ صدا انتخاب شد:\n\n"
            + VOICES[selected]["name"]
            + "\n\n"
            "حالا متن خودت را بفرست."
        )


# =========================
# TEXT HANDLER
# =========================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    # -------------------------
    # PERMANENT BUTTONS
    # -------------------------

    if text == "🇮🇷 فارسی":

        context.user_data["voice"] = "fa_farid"

        await update.message.reply_text(
            "🇮🇷 زبان فارسی انتخاب شد.\n\n"
            "حالا متن فارسی را بفرست.",
            reply_markup=main_menu()
        )

        return


    if text == "🇳🇱 صدای هلندی":

        context.user_data["voice"] = "nl_maarten"

        await update.message.reply_text(
            "🇳🇱 زبان هلندی انتخاب شد.\n\n"
            "Voice: Maarten\n\n"
            "حالا متن هلندی را بفرست.",
            reply_markup=main_menu()
        )

        return


    if text == "🇬🇧 صدای انگلیسی":

        context.user_data["voice"] = "en_guy"

        await update.message.reply_text(
            "🇬🇧 زبان انگلیسی انتخاب شد.\n\n"
            "Voice: Guy\n\n"
            "حالا متن انگلیسی را بفرست.",
            reply_markup=main_menu()
        )

        return


    if text == "🎙️ انتخاب صدای هلندی":

        await show_dutch_voices(
            update,
            context
        )

        return


    if text == "🎙️ انتخاب صدای انگلیسی":

        await show_english_voices(
            update,
            context
        )

        return


    # -------------------------
    # SPEED
    # -------------------------

    if text == "🐢 سرعت کمتر":

        context.user_data["speed"] = -1

        await update.message.reply_text(
            "🐢 سرعت روی «یک درجه کمتر» تنظیم شد.",
            reply_markup=main_menu()
        )

        return


    if text == "🎙️ سرعت معمولی":

        context.user_data["speed"] = 0

        await update.message.reply_text(
            "🎙️ سرعت روی حالت معمولی تنظیم شد.",
            reply_markup=main_menu()
        )

        return


    if text == "⚡ سرعت بیشتر":

        context.user_data["speed"] = 1

        await update.message.reply_text(
            "⚡ سرعت روی «یک درجه بیشتر» تنظیم شد.",
            reply_markup=main_menu()
        )

        return


    # -------------------------
    # GENERATE VOICE
    # -------------------------

    voice_key = context.user_data.get(
        "voice",
        DEFAULT_VOICE
    )

    speed = context.user_data.get(
        "speed",
        DEFAULT_SPEED
    )

    voice_info = VOICES[voice_key]

    await update.message.reply_text(
        "🎙️ در حال ساخت فایل صوتی..."
    )

    filename = (
        DOWNLOAD_DIR /
        f"voice_{int(time.time())}.mp3"
    )

    try:

        communicate = edge_tts.Communicate(

            text,

            voice_info["voice"],

            rate=get_rate(speed)

        )

        await communicate.save(
            str(filename)
        )

        with open(
            filename,
            "rb"
        ) as audio:

            await update.message.reply_audio(

                audio=audio,

                filename="voice.mp3",

                caption=(
                    "🎙️ "
                    + voice_info["name"]
                    + "\n"
                    + SPEEDS[speed]
                )

            )

        filename.unlink(
            missing_ok=True
        )

    except Exception as e:

        print(
            "VOICE ERROR:",
            repr(e)
        )

        await update.message.reply_text(

            "❌ خطا در ساخت فایل صوتی:\n\n"
            + str(e)
        )


# =========================
# MAIN
# =========================

def main():

    if not TOKEN:

        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing."
        )

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT &
            ~filters.COMMAND,
            text_handler
        )
    )

    print(
        "ALI VOICE PRO IS RUNNING..."
    )

    app.run_polling()


if __name__ == "__main__":
    main()
