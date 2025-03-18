import requests
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from db_manager import add_request_to_db
from dotenv import load_dotenv





# старт выбор города
async def weather(update:Update, context:CallbackContext):
    keyboard = [
        [InlineKeyboardButton('🏖️ Пхукет' ,callback_data='Phuket'), InlineKeyboardButton('🌆 Бангкок' ,callback_data='Bangkok') ],
        [InlineKeyboardButton('🏙️ Москва' ,callback_data='Moscow'), InlineKeyboardButton('🌉 Питер' ,callback_data='Saint Petersburg') ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выбери город", reply_markup=reply_markup)


# обработка города и вывод погоды
async def choose_city(update:Update, context:CallbackContext):
    query = update.callback_query    
    await query.answer()
    city = query.data
    weather_info, icon = await get_weather(city) 
    if icon:
        await update.callback_query.message.reply_photo(icon, caption=weather_info)
    else:
        await update.callback_query.message.reply_text(weather_info)

    username = update.callback_query.from_user.username
    full_name = update.callback_query.from_user.first_name
    add_request_to_db(username, full_name, 'Погода') 



# получаем погоду через АПИ
async def get_weather(city):
    load_dotenv()
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru'

    try:
        response = requests.get(url)
        answer = response.json()
        
        if "weather" in answer and "main" in answer:
            weather_icon = answer["weather"][0]["icon"]
            icon_url = f"https://openweathermap.org/img/wn/{weather_icon}@2x.png"
            return (
                f'🏙 Город: {answer["name"]}\n'
                f'☁ {answer["weather"][0]["description"].capitalize()}\n'
                f'🌡 Температура: {round(answer["main"]["temp"])}°C\n'
                f'🤔 Ощущается как: {round(answer["main"]["feels_like"])}°C\n',
                icon_url
            )
        else:
            return "❌ Ошибка: Не удалось получить данные о погоде."
        
    except requests.exceptions.RequestException as e:
        return f"🚫 Ошибка запроса: {e}"
    
