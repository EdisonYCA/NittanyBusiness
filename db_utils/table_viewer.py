import sqlite3

def print_names():
    connection = sqlite3.connect("../../db_backup/database.db")
    cursor = connection.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print("Tables in database:")
    for table in tables:
        print(table[0])

    connection.close()

def print_schema(table_name):
    connection = sqlite3.connect("../../db_backup/database.db")
    cursor = connection.cursor()

    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    schema = cursor.fetchone()

    if schema:
        print(f"Schema for table '{table_name}':")
        print(schema[0])
    else:
        print(f"No schema found for table '{table_name}'")

    connection.close()

def print_contents(table_name):
    connection = sqlite3.connect("../../db_backup/database.db")
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM {table_name} LIMIT 10;")
    rows = cursor.fetchall()

    print(f"\nFirst 10 rows of table '{table_name}':")
    for row in rows:
        print(row)

    # Count total number of rows
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    total_rows = cursor.fetchone()[0]

    print(f"\nTotal number of rows in '{table_name}': {total_rows}")

    connection.close()

if __name__ == '__main__':
    table_name = "Address"
    print_names()
    print_schema(table_name)
    print_contents(table_name)