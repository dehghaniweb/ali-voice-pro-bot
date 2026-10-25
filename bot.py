import os
import time
from pathlib import Path

import edge_tts

from telegram import (
    Update,
    BotCommand,
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
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID", "167186163")

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

    "fa_dilara": {
        "language": "fa",
        "name": "🇮🇷 فارسی - Dilara",
        "voice": "fa-IR-DilaraNeural",
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

    "nl_fenna": {
        "language": "nl",
        "name": "🇳🇱 Nederlands - Fenna",
        "voice": "nl-NL-FennaNeural",
    },

    # انگلیسی
    "en_guy": {
        "language": "en",
        "name": "🇺🇸 English - Guy",
        "voice": "en-US-GuyNeural",
    },

    "en_jenny": {
        "language": "en",
        "name": "🇺🇸 English - Jenny",
        "voice": "en-US-JennyNeural",
    },

    "en_aria": {
        "language": "en",
        "name": "🇺🇸 English - Aria",
        "voice": "en-US-AriaNeural",
    },

    "en_emma": {
        "language": "en",
        "name": "🇺🇸 English - Emma",
        "voice": "en-US-EmmaNeural",
    },

    "en_andrew": {
        "language": "en",
        "name": "🇺🇸 English - Andrew",
        "voice": "en-US-AndrewNeural",
    },

    "en_brian": {
        "language": "en",
        "name": "🇺🇸 English - Brian",
        "voice": "en-US-BrianNeural",
    },

    "en_sonia": {
        "language": "en",
        "name": "🇬🇧 English - Sonia",
        "voice": "en-GB-SoniaNeural",
    },

    "en_ryan": {
        "language": "en",
        "name": "🇬🇧 English - Ryan",
        "voice": "en-GB-RyanNeural",
    },

    "en_natasha": {
        "language": "en",
        "name": "🇦🇺 English - Natasha",
        "voice": "en-AU-NatashaNeural",
    },

    "en_william": {
        "language": "en",
        "name": "🇦🇺 English - William",
        "voice": "en-AU-WilliamNeural",
    },
}

DEFAULT_VOICES = {
    "fa": "fa_farid",
    "nl": "nl_maarten",
    "en": "en_guy",
}

LANGUAGE_NAMES = {
    "fa": "🇮🇷 فارسی",
    "nl": "🇳🇱 هلندی",
    "en": "🇬🇧 انگلیسی",
}

DEFAULT_VOICE = "fa_farid"
DEFAULT_SPEED = 0


# =========================
# SPEED
# =========================

SPEEDS = {
    -1: "🐢 آهسته",
    0: "🎙️ معمولی",
    1: "⚡ سریع",
}


def get_rate(speed):

    if speed == -1:
        return "-15%"

    if speed == 1:
        return "+15%"

    return "+0%"


# =========================
# MENU BUTTONS
# =========================

BTN_FA = "🇮🇷 فارسی"
BTN_NL = "🇳🇱 هلندی"
BTN_EN = "🇬🇧 انگلیسی"

BTN_VOICE_FA = "🎙️ صدای فارسی"
BTN_VOICE_NL = "🎙️ صدای هلندی"
BTN_VOICE_EN = "🎙️ صدای انگلیسی"

BTN_SLOW = "🐢 آهسته"
BTN_NORMAL = "🎙️ معمولی"
BTN_FAST = "⚡ سریع"

BTN_STATUS = "📊 وضعیت"
BTN_HELP = "❓ راهنما"
BTN_CLEAR = "🧹 پاک کردن پیام‌ها"


def main_menu():

    keyboard = [

        [BTN_FA, BTN_NL, BTN_EN],

        [BTN_VOICE_FA, BTN_VOICE_NL, BTN_VOICE_EN],

        [BTN_SLOW, BTN_NORMAL, BTN_FAST],

        [BTN_STATUS, BTN_HELP, BTN_CLEAR],

    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="متن خودت را بنویس..."
    )


# =========================
# HELPERS
# =========================

def current_voice_key(context):

    return context.user_data.get("voice", DEFAULT_VOICE)


def current_speed(context):

    return context.user_data.get("speed", DEFAULT_SPEED)


def select_voice(context, key):

    context.user_data["voice"] = key

    last = context.user_data.setdefault("last", {})

    last[VOICES[key]["language"]] = key


def select_language(context, language):

    last = context.user_data.get("last", {})

    key = last.get(
        language,
        DEFAULT_VOICES[language]
    )

    select_voice(context, key)

    return key


def status_text(context):

    key = current_voice_key(context)

    speed = current_speed(context)

    return (
        "📊 وضعیت فعلی\n\n"
        "🎙️ صدا:\n"
        + VOICES[key]["name"]
        + "\n\n"
        "⚡ سرعت:\n"
        + SPEEDS[speed]
    )


HELP_TEXT = (
    "❓ راهنما\n\n"
    "۱. زبان را با دکمه‌های بالا انتخاب کن.\n\n"
    "۲. اگر صدای دیگری می‌خواهی، یکی از دکمه‌های «صدا» را بزن.\n\n"
    "۳. سرعت را با «آهسته»، «معمولی» یا «سریع» تنظیم کن.\n\n"
    "۴. متن را بفرست تا فایل صوتی بسازم."
)


# =========================
# INLINE VOICE MENU
# =========================

def build_voice_buttons(language, current):

    buttons = []

    for key, info in VOICES.items():

        if info["language"] == language:

            label = info["name"]

            if key == current:
                label = "✅ " + label

            buttons.append([
                InlineKeyboardButton(
                    label,
                    callback_data="voice_" + key
                )
            ])

    return InlineKeyboardMarkup(buttons)


async def show_voices(update, context, language):

    await update.message.reply_text(
        "🎙️ صدای "
        + LANGUAGE_NAMES[language]
        + " را انتخاب کن:",
        reply_markup=build_voice_buttons(
            language,
            current_voice_key(context)
        )
    )


# =========================
# COMMANDS
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["voice"] = DEFAULT_VOICE
    context.user_data["speed"] = DEFAULT_SPEED

    await update.message.reply_text(
        "🎙️ Ali Voice Pro\n\n"
        "متن را به صدا تبدیل می‌کنم:\n\n"
        "🇮🇷 فارسی\n"
        "🇳🇱 هلندی\n"
        "🇬🇧 انگلیسی\n\n"
        "زبان را انتخاب کن و متن را بفرست.",
        reply_markup=main_menu()
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        status_text(context),
        reply_markup=main_menu()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        HELP_TEXT,
        reply_markup=main_menu()
    )


# =========================
# CLEAR CHAT
# =========================

async def clear_chat(bot, chat_id, last_id, limit=2000):

    first = max(1, last_id - limit)

    ids = list(range(last_id, first - 1, -1))

    for i in range(0, len(ids), 100):

        batch = ids[i:i + 100]

        try:

            await bot.delete_messages(
                chat_id=chat_id,
                message_ids=batch
            )

        except Exception as e:

            print("CLEAR ERROR:", repr(e))


# =========================
# BUTTON HANDLER (inline)
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    if data == "clear_no":

        await query.edit_message_text(
            "❌ پاک کردن لغو شد."
        )

        return

    if data == "clear_yes":

        chat_id = query.message.chat_id

        last_id = query.message.message_id

        await clear_chat(
            context.bot,
            chat_id,
            last_id
        )

        await context.bot.send_message(
            chat_id=chat_id,
            text="🧹 پیام‌ها پاک شد.",
            reply_markup=main_menu()
        )

        return

    if not data.startswith("voice_"):
        return

    selected = data.replace("voice_", "", 1)

    if selected not in VOICES:
        return

    select_voice(context, selected)

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

    if not text:
        return

    # ---- language buttons ----

    language_buttons = {
        BTN_FA: "fa",
        BTN_NL: "nl",
        BTN_EN: "en",
    }

    if text in language_buttons:

        language = language_buttons[text]

        key = select_language(context, language)

        await update.message.reply_text(
            LANGUAGE_NAMES[language]
            + " انتخاب شد.\n\n"
            "🎙️ صدا:\n"
            + VOICES[key]["name"]
            + "\n\n"
            "حالا متن را بفرست.",
            reply_markup=main_menu()
        )

        return

    # ---- voice choice buttons ----

    voice_buttons = {
        BTN_VOICE_FA: "fa",
        BTN_VOICE_NL: "nl",
        BTN_VOICE_EN: "en",
    }

    if text in voice_buttons:

        await show_voices(
            update,
            context,
            voice_buttons[text]
        )

        return

    # ---- speed buttons ----

    speed_buttons = {
        BTN_SLOW: -1,
        BTN_NORMAL: 0,
        BTN_FAST: 1,
    }

    if text in speed_buttons:

        context.user_data["speed"] = speed_buttons[text]

        await update.message.reply_text(
            "⚡ سرعت تنظیم شد:\n\n"
            + SPEEDS[speed_buttons[text]],
            reply_markup=main_menu()
        )

        return

    # ---- status / help ----

    if text == BTN_STATUS:

        await status_command(update, context)

        return

    if text == BTN_HELP:

        await help_command(update, context)

        return

    if text == BTN_CLEAR:

        confirm = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "✅ بله، پاک کن",
                callback_data="clear_yes"
            ),
            InlineKeyboardButton(
                "❌ لغو",
                callback_data="clear_no"
            ),
        ]])

        await update.message.reply_text(
            "🧹 پیام‌های این چت پاک شوند؟\n\n"
            "فقط پیام‌های ۴۸ ساعت اخیر پاک می‌شوند "
            "و این کار برگشت ندارد.",
            reply_markup=confirm
        )

        return

    # ---- generate voice ----

    voice_key = current_voice_key(context)

    speed = current_speed(context)

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

        with open(filename, "rb") as audio:

            await update.message.reply_audio(
                audio=audio,
                filename="voice.mp3",
                caption=(
                    "🎙️ "
                    + voice_info["name"]
                    + "\n"
                    + SPEEDS[speed]
                ),
                reply_markup=main_menu()
            )

        filename.unlink(missing_ok=True)

    except Exception as e:

        print("VOICE ERROR:", repr(e))

        await update.message.reply_text(
            "❌ خطا در ساخت فایل صوتی:\n\n"
            + str(e),
            reply_markup=main_menu()
        )


# =========================
# STARTUP
# =========================

async def post_init(app):

    await app.bot.set_my_commands([
        BotCommand("start", "شروع و نمایش منو"),
        BotCommand("status", "وضعیت صدا و سرعت"),
        BotCommand("help", "راهنما"),
    ])

    try:

        await app.bot.send_message(
            chat_id=int(OWNER_CHAT_ID),
            text=(
                "✅ ربات روشن شد.\n\n"
                "زبان را انتخاب کن و متن را بفرست."
            ),
            reply_markup=main_menu()
        )

    except Exception as e:

        print("STARTUP MESSAGE ERROR:", repr(e))


def main():

    if not TOKEN:

        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing."
        )

    app = (
        Application
        .builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    )

    print("ALI VOICE PRO IS RUNNING...")

    app.run_polling()


if __name__ == "__main__":
    main()
