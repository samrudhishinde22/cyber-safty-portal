import sqlite3

# Simple DB initializer without depending on Flask app to avoid circular import.
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
);
''')
conn.commit()
conn.close()
print("Database 'users.db' created (if not existed) and users table ready.")