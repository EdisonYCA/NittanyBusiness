import pandas as pd
import sqlite3
import os
import hashlib
from glob import glob

def init_db():
    db_path = "..//database.db"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    #standin statement for table creation - one for each table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL
            );
        """)

    static_backup = ".\\static_backup\\"
    csv_files = glob(os.path.join(static_backup, "*.csv"))

    print(f"Found {len(csv_files)} CSV files(s) in {static_backup}.......................")

    for file in csv_files:
        print(f"Processing {file}")
        df = pd.read_csv(file)

        #TODO verify this pulls the right part of the filename
        table_name = os.path.splitext(os.path.basename(file))[0]
        if table_name == "Users":
            #dev team agrees on SHA 256 hashing
            df['password'] = df['password'].apply(lambda pwd: hashlib.sha256(pwd.encode('utf-8)')).hexdigest())
        else:
            continue

        df.to_sql(table_name, connection, if_exists='append', index=False)
        print("Inserted data into table '{table_name}'.")


    connection.commit()
    connection.close()
    print("Database initialized.")

if __name__ == '__main__':
    init_db()