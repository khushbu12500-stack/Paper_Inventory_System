import os
import mysql.connector

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "khushbu@060626"),
    database=os.getenv("DB_NAME", "paper_inventory_db"),
    port=int(os.getenv("DB_PORT", 3306))
)

cursor = conn.cursor(buffered=True)

print("Database Connected Successfully")