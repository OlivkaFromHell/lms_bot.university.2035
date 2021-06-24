import json
import sqlite3

conn = sqlite3.connect("data/user_database.db")
cursor = conn.cursor()

with open('data/user_report.json', 'rb') as f:
    traffic = json.load(f)

telegram_id = 123

for note in traffic:
    if note['email'] == 'alimov.rn@edu.spbstu.ru':
        print(note['id'], note['lastname'], note['firstname'], note['email'])
        info = [(telegram_id, note['id'], note['lastname'], note['firstname'], note['email'])]
        cursor.executemany("INSERT INTO user_db VALUES (?,?,?,?,?)", info)
        conn.commit()