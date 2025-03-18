import sqlite3
import config


conn=sqlite3.connect(config.DB_PATH)
cursor = conn.cursor()



cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        full_name TEXT NOT NULL,                       
        request_type TEXT NOT NULL,       
        timestamp TIMESTAMP DEFAULT (strftime('%d-%m-%Y %H:%M:%S', 'now', 'localtime'))
               )
               ''')

conn.close()


