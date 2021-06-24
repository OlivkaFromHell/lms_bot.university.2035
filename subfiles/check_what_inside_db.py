import sqlite3

conn = sqlite3.connect("data/user_database.db")
cursor = conn.cursor()

sql = "SELECT moodle_id FROM user_db WHERE email = 'vadim.tvj@gmail.com'"

cursor.execute(sql)
print(cursor.fetchone()[0])