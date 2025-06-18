# insert_test_data.py
from db import get_db

db = get_db()
cur = db.cursor()

# Insert test author
cur.execute("""
    INSERT INTO authors (name, password, email, is_admin)
    VALUES (%s, %s, %s, %s)
    RETURNING id
""", ("Alice", "securepass123", "alice@example.com", 1))
author_id = cur.fetchone()['id']

# Insert test post
cur.execute("""
    INSERT INTO posts (title, content, author_id, author_name)
    VALUES (%s, %s, %s, %s)
""", ("My First Post", "Hello world!", author_id, "Alice"))

db.commit()
print("✅ Test data inserted!")