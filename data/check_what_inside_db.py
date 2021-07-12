import sqlite3

conn = sqlite3.connect("user_database.db")
cursor = conn.cursor()

sql = "SELECT * FROM user_db"

cursor.execute(sql)

# смотрим заголовки таблицы
print(list(map(lambda x: x[0], cursor.description)))

for row in cursor.fetchall():
    print(row)

# sql = "DELETE FROM user_db WHERE telegram_id = 296512517"
#
# cursor.execute(sql)
# conn.commit()
