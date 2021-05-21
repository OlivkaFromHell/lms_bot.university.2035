import sqlite3

conn = sqlite3.connect("data/user_database.db")
cursor = conn.cursor()

sql = "SELECT * FROM user_db"

cursor.execute(sql)
print(cursor.fetchall())