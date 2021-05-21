import sqlite3

conn = sqlite3.connect("data/user_database.db")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS  user_db 
                  (telegram_id INTEGER,
                   moodle_id text, lastname text, firstname text, email text UNIQUE)
               """)


# users = [(0, 1, 'Rashid', 'Alimov', 'alimov.rn@edu.spbstu.ru'),
#          (0, 1, 'Nataly', 'Yakushkina', 'yakushkina.na@edu.spbstu.ru'),
#          (0, 3, 'Vadim', 'last_name', 'tregubenko.vyu@edu.spbstu.ru')]
#
# cursor.executemany("INSERT INTO user_db VALUES (?,?,?,?,?)", users)
# conn.commit()


