import sqlite3

# Connect to your SQLite database
connection = sqlite3.connect(r'C:\\Users\dipak\Desktop\Assignment\database_service\\instance\db.sqlite3')
cursor = connection.cursor()

# Fetch all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Loop through all tables and delete all rows from each
for table in tables:
    table_name = table[0]
    print(f"Deleting all rows from {table_name}")
    cursor.execute(f"DELETE FROM {table_name};")

# Commit changes and close the connection
connection.commit()
connection.close()

print("All rows from all tables have been deleted.")
