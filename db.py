import sqlite3

conn = sqlite3.connect('career_system.db')
cursor = conn.cursor()

# View all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# View data from a specific table
cursor.execute("SELECT * FROM user_profiles;")
rows = cursor.fetchall()
for row in rows:
    print(row)

# Add this to your db.py to see table contents
cursor.execute("SELECT * FROM user_profiles;")
rows = cursor.fetchall()
print("Data in user_profiles:", rows)
conn.close()