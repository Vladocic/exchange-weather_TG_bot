import sqlite3
import config
import os
from db_manager import add_request_to_db
from telegram import Update, BotCommand
from telegram.ext import CallbackContext
from PIL import Image, ImageDraw, ImageFont


def set_bot_commands(application):
    commands = [
        ("start", "Запустить бота"),
        ("exchange", "Конвертер валют"),
        ("history", "История запросов"),
        ("weather", "Узнать погоду"),
        ("horoscope", "Ваш гороскоп"),
    ]
    application.bot.set_my_commands([BotCommand(cmd, desc) for cmd, desc in commands])





async def start(update:Update, context:CallbackContext):
    context.user_data["waiting_for_amount"] = False
    username = update.message.from_user.username
    full_name = update.message.from_user.first_name
    add_request_to_db(username, full_name, 'Запуск бота') 
    await update.message.reply_text("Привет! Я Telegram-бот. Введите любое сообщение.")




async def history(update:Update, context:CallbackContext):
    context.user_data["waiting_for_amount"] = False

    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username, full_name, request_type, timestamp FROM user_requests ORDER BY id DESC LIMIT 10')
        rows = cursor.fetchall()

    if not rows:
        await update.message.reply_text("📜 История запросов пуста")
        return

    header = ['Username', 'Full', 'Request', 'Time']


    column_widths = [0, 0, 0, 0] 

    for_column = rows.copy()
    for_column.append(tuple(header))
 
    for a,b,c,d in for_column:
        column_widths[0] = max(column_widths[0], len(a))
        column_widths[1] = max(column_widths[1], len(b)) 
        column_widths[2] = max(column_widths[2], len(c)) 
        column_widths[3] = max(column_widths[3], len(d)) 
    
    column_widths = [i*8 for i in column_widths]    

    table_data = [header] + rows



    width =  sum(column_widths)
    height = len(table_data) * 25

    img = Image.new("RGB", (width,height), "white")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("Arial.ttf", 11)
    except IOError:    
        font = ImageFont.load_default()

    x, y = 20, 20

    for i, text in enumerate(header):
        draw.text((x + sum(column_widths[:i]), y), text, font=font, fill="black")
 
    draw.line(xy= [(x,y+15),(sum(column_widths)-((column_widths[3])/4), y+15)], fill='black', width= 2)
    
    y+=20


    for row in rows:
        for i, text in enumerate(row):
            draw.text((x + sum(column_widths[:i]), y), text, font=font, fill="black" )
        y+=20

    for i  in range(1, len(column_widths)):
        draw.line([(x+sum(column_widths[:i])*0.95,10),(x+sum(column_widths[:i])*0.95,y)], fill='black', width=2 )


    img_path = "history.png"
    img.save(img_path)

    with open(img_path, "rb") as photo:
        await update.message.reply_photo(photo)
    
    os.remove(img_path)