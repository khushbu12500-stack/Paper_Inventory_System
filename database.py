import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="khushbu@060626",
    database="paper_inventory_db"
)

cursor = conn.cursor(buffered=True)

print("Database Connected Successfully")