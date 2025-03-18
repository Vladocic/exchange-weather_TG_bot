import requests
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from db_manager import add_request_to_db



# первые кнопки по обмену
async def exchange(update:Update, context:CallbackContext):
    keyboard = [
        [InlineKeyboardButton("💰 Хочу получить", callback_data = "want_to_get_money")],
        [InlineKeyboardButton("💵 У меня есть", callback_data = "have_money")]
        ]  
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Выберите действие:", reply_markup=reply_markup)


# обработка кнопок по обмену
async def button_handler(update:Update, context:CallbackContext):
    query = update.callback_query
    await query.answer()

    currency_mode = {
        "want_to_get_money":1,
        "have_money":2
    }

    if query.data in currency_mode:
        context.user_data["main_currency"] = currency_mode[query.data]
        text = "Введите сумму, которую хотите получить:" if query.data == "want_to_get_money" else "Введите сумму, которая у вас есть:"

    context.user_data["waiting_for_amount"] = True
    await query.message.reply_text(text)


# вводим сумму для обмена
async def amount_input(update:Update, context:CallbackContext):
    if not context.user_data.get("waiting_for_amount"):
        return
    number = update.message.text.strip()
    check_number= re.fullmatch(r'\d+([.,]\d+)?$',number)

    if check_number:
        context.user_data["waiting_for_amount"] = False
        if '.' in number or ',' in number:
            context.user_data["amount"] = float(re.sub(r'[.,]', '.', number))
        else:
            context.user_data["amount"] = int(number)        
        await choose_currency(update, context)    

    else:
        await update.message.reply_text("🚫 Ошибка! Вы указали не число, введите ещё раз.")



# показываем кнопки выбора валюс с и на что
async def choose_currency(update:Update, context:CallbackContext):

    keyboard = [
        [InlineKeyboardButton("🇷🇺 Рубли", callback_data="from_rub"), InlineKeyboardButton("🇷🇺 Рубли", callback_data="to_rub")],
        [InlineKeyboardButton("🇺🇸 Доллары", callback_data="from_usd"), InlineKeyboardButton("🇺🇸 Доллары", callback_data="to_usd")],
        [InlineKeyboardButton("🇹🇭 Баты", callback_data="from_thb"), InlineKeyboardButton("🇹🇭 Баты", callback_data="to_thb")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("   💸 Меняю:                 💰 Получаю:", reply_markup=reply_markup)
 




# обрбаотка кнопка выбора валют - нажать 2 кнопки
async def currency_choice(update:Update, context:CallbackContext):
    if context.user_data["waiting_for_amount"] == False:

        query = update.callback_query
        await query.answer()
        currency_mapping = {
            'from_rub':'RUB',
            'from_usd':'USD',
            'from_thb':'THB',
            'to_rub':'RUB',
            'to_usd':'USD',
            'to_thb':'THB'
        }

        if query.data.startswith('from'):
            context.user_data['from'] = currency_mapping[query.data]
        elif query.data.startswith('to'):
            context.user_data['to'] = currency_mapping[query.data]

        from_currency = context.user_data.get('from')   
        to_currency = context.user_data.get('to') 
        sum_to_change = context.user_data.get('amount', 0) 

        if from_currency and to_currency:
            text = f'{from_currency} чтобы получить {sum_to_change} {to_currency}' if context.user_data['main_currency'] == 1 else f'{sum_to_change} {from_currency} на {to_currency}'
            await query.message.reply_text(f'Вы меняете {text}')
            await get_exchange_rate(update,from_currency, to_currency)
            await calculate_exchange(update,context)
            await repeat_exchange(update,context)
            return

        else:
            await query.message.reply_text('Выберите вторую валюту')


# кнопки на новый обмен
async def repeat_exchange(update:Update, context:CallbackContext):
    key_board = [[InlineKeyboardButton("Да", callback_data = 'Yes')], [InlineKeyboardButton("Нет", callback_data = 'No')]]
    reply_markup = InlineKeyboardMarkup(key_board)
    await update.callback_query.message.reply_text("Сделать нвый обмен?", reply_markup=reply_markup )

# обработка потворных кнопок
async def new_exchange(update:Update, context:CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "Yes":
        await exchange(update, context)
    else:
        await query.message.reply_text("Всего хорошего!")


# получаем курс АПИ
async def get_exchange_rate(update:Update, from_currency, to_currency):
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"

    try:
        response = requests.get(url)
        data = response.json()
        if 'rates' in data and to_currency in data["rates"]:
            return data['rates'][to_currency]
        else:
            await update.message.reply_text(f"❌ Курс для {to_currency} не найден.")
            return None
        
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f'❌ Ошибка запроса: {e}')
        return None
    except ValueError:
        await update.message.reply_text("❌ Ошибка обработки данных от API. Попробуйте позже.")
        return None




# считаем курс и значения и выводим результат
async def calculate_exchange(update: Update, context: CallbackContext):
    from_currency = context.user_data.get('from')   
    to_currency = context.user_data.get('to') 
    amount = context.user_data.get('amount', 0) 

    if not from_currency or not to_currency or amount == 0:
        await update.message.reply_text("❌ Ошибка! Не выбраны валюты или сумма.")
        return

    rate = await get_exchange_rate(update, from_currency, to_currency)
    if rate is None:
        return
    
    
    converted_amount = round(amount * rate,2) if context.user_data["main_currency"] == 2 else round(amount/rate,2) 

    if context.user_data["main_currency"] == 2:
        text = f"💰 Вы меняете {amount} {from_currency} и получаете {converted_amount} {to_currency}"
    else:
        text = f"Вам нужно {converted_amount} {from_currency}, чтобы получить 💰 {amount} {to_currency}"

    await update.callback_query.message.reply_text(f"💱 Курс {from_currency} → {to_currency}: {rate}\n{text}")

    context.user_data.clear()

    username = update.callback_query.from_user.username
    full_name = update.callback_query.from_user.first_name
    add_request_to_db(username, full_name, 'Обмен валюты') 











