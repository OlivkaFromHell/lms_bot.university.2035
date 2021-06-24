import sqlite3

conn = sqlite3.connect("data/user_database.db")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS  user_db 
                  (telegram_id INTEGER UNIQUE,
                   moodle_id INTEGER, fullname text, email text)
               """)

