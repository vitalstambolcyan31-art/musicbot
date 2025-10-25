import telebot
import requests

# 🔹 Вставь сюда свой токен от BotFather
TOKEN = "8372930034:AAFVPhVEcsWLxNONkcbmpzVYXI2K0Z2Oiu8"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎵 Привет! Отправь название песни, и я найду несколько вариантов 🎧")

@bot.message_handler(func=lambda message: True)
def search_music(message):
    query = message.text.strip()
    if not query:
        bot.reply_to(message, "⚠️ Напиши название песни или исполнителя.")
        return

    bot.send_chat_action(message.chat.id, 'typing')

    url = f"https://itunes.apple.com/search?term={query}&limit=5"
    response = requests.get(url)

    if response.status_code != 200:
        bot.reply_to(message, "❌ Ошибка при поиске, попробуй позже.")
        return

    data = response.json()
    results = data.get("results", [])

    if not results:
        bot.reply_to(message, "😕 Ничего не найдено. Попробуй другое название.")
        return

    reply = "🎧 Нашёл несколько песен:\n\n"
    for track in results:
        track_name = track.get("trackName", "Без названия")
        artist = track.get("artistName", "Неизвестен")
        preview = track.get("previewUrl", None)
        if preview:
            reply += f"🎵 *{track_name}* — {artist}\n▶️ [Слушать]({preview})\n\n"

    bot.send_message(message.chat.id, reply, parse_mode="Markdown")

print("Бот запущен...")
bot.polling(none_stop=True)
