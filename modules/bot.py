import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from flask_mongoengine import MongoEngine
from mongoengine import disconnect
from asgiref.sync import sync_to_async

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Flask + MongoDB setup
db = MongoEngine()
app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'places_db',
    'host': 'mongodb://db:27017/places_db'
}
app.config['SECRET_KEY'] = 'super_secret_key_12345'
disconnect(alias='default')
db.init_app(app)

# Імпорт моделей (UserModel і PlaceModel повинні бути у файлі models.py)
from models import UserModel, PlaceModel

# Асинхронні обгортки для роботи з базою
@sync_to_async
def get_registered_user(username):
    return UserModel.objects(telegram=username).first()

@sync_to_async
def update_chat_id(user, chat_id):
    user.telegram_chat_id = str(chat_id)
    user.save()

@sync_to_async
def search_places(user, keyword):
    # Пошук по імені (незалежно від регістру)
    return list(PlaceModel.objects(user=user, name__icontains=keyword))

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username
    chat_id = update.effective_chat.id

    if not username:
        await update.message.reply_text("❌ У тебе не вказано Telegram username!")
        return

    user_obj = await get_registered_user(username)
    if not user_obj:
        await update.message.reply_text("❌ Тебе немає в базі. Зареєструй свій Telegram username на сайті.")
        return

    # Збережемо юзера в контекст для подальшого використання
    context.user_data['user_obj'] = user_obj
    await update_chat_id(user_obj, chat_id)

    # Відправляємо кнопку
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("Отримати мої місця")]],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await update.message.reply_text(
        f"✅ Привіт, @{user_obj.telegram}! Натисни кнопку нижче, щоб переглянути свої місця.",
        reply_markup=keyboard
    )

# Обробка текстових повідомлень
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_obj = context.user_data.get('user_obj')

    if not user_obj:
        await update.message.reply_text("❌ Спочатку введи команду /start.")
        return

    # Якщо користувач натиснув кнопку "Отримати мої місця"
    if text == "Отримати мої місця":
        # Помічаємо, що тепер чекаємо ключове слово
        context.user_data['expecting_keyword'] = True
        await update.message.reply_text("🔍 Введіть ключове слово для пошуку ваших місць:")
        return

    # Якщо бот чекає на ключове слово
    if context.user_data.get('expecting_keyword', False):
        context.user_data['expecting_keyword'] = False
        keyword = text
        await search_and_send_places(update, context, user_obj, keyword)
        return

    # Якщо повідомлення не відповідає очікуваному — показуємо підказку
    await update.message.reply_text("Невідома команда. Натисни кнопку нижче або введи /start заново.")

# Пошук місць і відправка результатів
async def search_and_send_places(update: Update, context: ContextTypes.DEFAULT_TYPE, user_obj, keyword: str):
    chat_id = update.effective_chat.id
    await update_chat_id(user_obj, chat_id)

    places = await search_places(user_obj, keyword)

    if not places:
        await update.message.reply_text("❌ Нічого не знайдено за цим словом.")
        return

    for place in places:
        if not place.image:
            continue

        caption = (
            f"<b>{place.name}</b>\n"
            f"⭐️ Рейтинг: {place.rating}\n"
            f"📍 Адреса: {place.full_address}\n"
            f"🏷 Тип: {place.place_type}\n"
            f"📞 Телефон: {place.phone}\n"
            f"🌐 Вебсайт: {place.website}"
        )

        await update.message.reply_photo(
            photo=place.image,
            caption=caption,
            parse_mode="HTML"
        )

# Точка входу
if __name__ == "__main__":
    TELEGRAM_BOT_TOKEN = "7600737352:AAHpzQQXfoaUOC6ZxJyUIYd3RwpMhX6xWXM"

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.run_polling()

