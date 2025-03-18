import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from db_manager import add_request_to_db
from deep_translator import GoogleTranslator



# старт - показываем кнопки
async def horoscope(update:Update, context:CallbackContext):
    zodiac_signs= [
        ("♈ Овен", "zodiac_aries"), ("♉ Телец", "zodiac_taurus"), ("♊ Близнецы", "zodiac_gemini"),
    ("♋ Рак", "zodiac_cancer"), ("♌ Лев", "zodiac_leo"), ("♍ Дева", "zodiac_virgo"),
    ("♎ Весы", "zodiac_libra"), ("♏ Скорпион", "zodiac_scorpio"), ("♐ Стрелец", "zodiac_sagittarius"),
    ("♑ Козерог", "zodiac_capricorn"), ("♒ Водолей", "zodiac_aquarius"), ("♓ Рыбы", "zodiac_pisces")
    ]
    keyboard = []
    row = []

    for i, (name, value) in enumerate(zodiac_signs, start = 1):
        row.append(InlineKeyboardButton(name,callback_data=value))
        if i%3==0:
            keyboard.append(row)
            row = []

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Ваш знак зодиака:", reply_markup=reply_markup)


# обрбаотка кнопок и показ гороскопа
async def handle_horoscope_choice (update:Update, context:CallbackContext):
    query = update.callback_query
    await query.answer()

    zodiac_translation = {
        "aries": "Овен", "taurus": "Телец", "gemini": "Близнецы",
        "cancer": "Рак", "leo": "Лев", "virgo": "Дева",
        "libra": "Весы", "scorpio": "Скорпион", "sagittarius": "Стрелец",
        "capricorn": "Козерог", "aquarius": "Водолей", "pisces": "Рыбы"
    }

    if query.data.startswith('zodiac_'):
        sign = query.data.split('_')[1]
        context.user_data['zodiac_sign'] = sign
        await query.message.reply_text(f"Вы выбрали знак: {zodiac_translation[sign]}")  # Уведомляем пользователя
        horoscope = await get_horoscope(sign)
        await query.message.reply_text(horoscope)
        
        username = query.from_user.username
        full_name = query.from_user.first_name
        await add_request_to_db(username, full_name, 'Гороскоп')


    else:
        await query.message.reply_text("❌ Ошибка! Некорректный знак зодиака.")
        


# формируем гороскоп (апи запрос)
async def get_horoscope(sign):
   
    url = f'https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={sign}&day=TODAY'

    try:
        response = requests.get(url)
        answer= response.json().get('data')

        if 'date' in answer and 'horoscope_data' in answer:
            return (f"🔮 Ваш гороскоп на {answer['date']}:\n\n"
                            f"{GoogleTranslator(source='auto', target='ru').translate(answer['horoscope_data'])}\n\n"
                            f"✨ Прекрасного дня!")
        else:
            return "⚠️ Не удалось получить гороскоп. Попробуйте позже."


    except requests.exceptions.RequestException as e:
        return f"🚫 Ошибка запроса: {e}"


    