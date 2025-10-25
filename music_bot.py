import os
import uuid
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8372930034:AAFVPhVEcsWLxNONkcbmpzVYXI2K0Z2Oiu8"

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я помогу тебе найти музыку.\n\n"
        "🎧 Напиши название песни или исполнителя — и я покажу список."
    )

# --- Поиск песен ---
async def search_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    await update.message.reply_text(f"🔍 Ищу: {query}...")

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']

        buttons = []
        for i, entry in enumerate(results[:5]):
            title = entry['title'][:60]
            video_id = entry['id']
            buttons.append([InlineKeyboardButton(f"🎵 {title}", callback_data=video_id)])

        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Выбери песню:", reply_markup=reply_markup)

    except Exception as e:
        print("Ошибка поиска:", e)
        await update.message.reply_text("❌ Не удалось найти. Попробуй другое название.")

# --- Обработка выбора ---
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    video_id = query.data
    await query.edit_message_text("🎧 Скачиваю выбранную песню...")

    tmp_name = f"track_{uuid.uuid4().hex}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': tmp_name + '.%(ext)s',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
            filename = ydl.prepare_filename(info)
            filename = os.path.splitext(filename)[0] + ".mp3"

            await query.message.reply_audio(
                audio=open(filename, 'rb'),
                title=info.get('title', 'Music'),
                caption="✅ Готово! 🎶"
            )
            os.remove(filename)
    except Exception as e:
        print("Ошибка загрузки:", e)
        await query.message.reply_text("❌ Не удалось скачать трек.")

# --- Запуск ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("✅ Бот запущен! Напиши ему в Telegram.")
    app.run_polling()

if __name__ == "__main__":
    main()
