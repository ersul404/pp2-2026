import psycopg2

conn = psycopg2.connect(
    dbname="your_db",
    user="your_user",
    password="your_pass",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# Вызов процедуры
cur.execute("CALL upsert_contact(%s, %s)", ('Ersultan', '87771234567'))

# Вызов функции
cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", ('er',))
rows = cur.fetchall()

for row in rows:
    print(row)

conn.commit()
cur.close()
conn.close()