"""Check SQLite database schema."""
import sqlite3

path = r"C:\Users\divya.bajaj_jadeglob\Downloads\DB.Browser.for.SQLite-v3.13.1-win32\HackthonTest.db"
conn = sqlite3.connect(path)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print("Tables:", [t[0] for t in tables])
for t in tables:
    c.execute(f'PRAGMA table_info("{t[0]}")')
    cols = c.fetchall()
    print(f"\n{t[0]}:", [(x[1], x[2]) for x in cols])
conn.close()
