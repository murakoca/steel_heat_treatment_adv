import sqlite3
conn=sqlite3.connect('materials.db')
conn.execute('CREATE TABLE IF NOT EXISTS steels (name TEXT, composition TEXT)')
conn.commit()
conn.close()