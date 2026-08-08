import sqlite3

conn = sqlite3.connect("metro.db")

cursor = conn.cursor()

cursor.execute("PRAGMA table_info(booking)")

for row in cursor.fetchall():
    print(row)

conn.close()
