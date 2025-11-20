import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
import google.generativeai as genai
from datetime import datetime, timedelta

TELEGRAM_TOKEN = "API_KEY"
GEMINI_API_KEY = "API_KEY"

genai.configure(api_key=GEMINI_API_KEY)

models = genai.list_models()
model = genai.GenerativeModel('gemini-2.5-flash', generation_config={
    'temperature': 0.7,
    'top_p': 0.8,
    'top_k': 40,
})


user_last_message = {}




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот с интеграцией Gemini AI. Задайте мне любой вопрос, и я постараюсь на него ответить!"
    )




async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        current_time = datetime.now()

      
        if user_id in user_last_message:
            time_diff = current_time - user_last_message[user_id]
            if time_diff.total_seconds() < 3:  
                return

       
        user_last_message[user_id] = current_time

      
        await update.message.chat.send_action(action=ChatAction.TYPING)

 
        user_message = update.message.text

        # Получаем ответ от Gemini
        response = model.generate_content(user_message)

       
        if response and hasattr(response, 'text'):
            await update.message.reply_text(response.text)
        else:
            print("Response:", response)  
            await update.message.reply_text("Извините, не удалось сгенерировать ответ. Попробуйте переформулировать вопрос.")
    except Exception as e:
        print(f"Debug - Error: {str(e)}") 
        await update.message.reply_text(f"Произошла ошибка при обработке запроса. Попробуйте позже.")


def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

 
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
