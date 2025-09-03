import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
import google.generativeai as genai
from datetime import datetime, timedelta

# Конфигурация API ключей
TELEGRAM_TOKEN = "8442749835:AAH0wpmfMpAY7A5xIghRWyt1O_UX9uaBEzI"
GEMINI_API_KEY = "AIzaSyBjQh_PBUFvbwEHPyCgwHmwymJi9ZDz4bo"

# Настройка Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# Получаем список доступных моделей
models = genai.list_models()
model = genai.GenerativeModel('gemini-2.5-flash', generation_config={
    'temperature': 0.7,
    'top_p': 0.8,
    'top_k': 40,
})

# Словарь для хранения времени последнего сообщения от пользователя
user_last_message = {}

# Обработчик команды /start


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот с интеграцией Gemini AI. Задайте мне любой вопрос, и я постараюсь на него ответить!"
    )

# Обработчик текстовых сообщений


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        current_time = datetime.now()

        # Проверяем, не было ли недавнего сообщения от этого пользователя
        if user_id in user_last_message:
            time_diff = current_time - user_last_message[user_id]
            if time_diff.total_seconds() < 3:  # Защита от спама: минимум 3 секунды между сообщениями
                return

        # Обновляем время последнего сообщения
        user_last_message[user_id] = current_time

        # Показываем индикатор набора текста
        await update.message.chat.send_action(action=ChatAction.TYPING)

        # Получаем вопрос от пользователя
        user_message = update.message.text

        # Получаем ответ от Gemini
        response = model.generate_content(user_message)

        # Проверяем, есть ли ответ
        if response and hasattr(response, 'text'):
            # Отправляем ответ пользователю
            await update.message.reply_text(response.text)
        else:
            print("Response:", response)  # для отладки
            await update.message.reply_text("Извините, не удалось сгенерировать ответ. Попробуйте переформулировать вопрос.")
    except Exception as e:
        print(f"Debug - Error: {str(e)}")  # для отладки
        await update.message.reply_text(f"Произошла ошибка при обработке запроса. Попробуйте позже.")


def main():
    # Создаем и настраиваем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
