import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from dotenv import load_dotenv
from handlers import *

# Загружаем токен
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ Токен бота не найден! Проверь .env файл.")

logging.basicConfig(filename="bot.log", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR)





def main():
    app = Application.builder().token(BOT_TOKEN).build()

    set_bot_commands(app)


    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("exchange", exchange))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("horoscope", horoscope))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, amount_input))
    app.add_handler(CallbackQueryHandler(currency_choice, pattern="^(from_|to_)"))
    app.add_handler(CallbackQueryHandler(choose_city, pattern="^(Phuket|Moscow|Bangkok|Saint Petersburg)"))
    app.add_handler(CallbackQueryHandler(handle_horoscope_choice, pattern="^(zodiac_)"))
    app.add_handler(CallbackQueryHandler(new_exchange, pattern="^(Yes|No)"))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot is running!")
    
    app.run_polling()  # ✅ Запускаем бота

if __name__ == "__main__":
    main()
   