import sqlite3
import config 

def add_request_to_db(username='Unknown user', full_name='No name', request_type='Unknow request'):
    con = sqlite3.connect(config.DB_PATH)
    cursor = con.cursor()
    cursor.execute('''
        INSERT INTO user_requests(username, full_name, request_type)
        VALUES (?, ?, ?)
    ''', (username,full_name,request_type))
    con.commit()
    con.close()
    


