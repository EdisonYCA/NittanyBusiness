import pandas as pd
import sqlite3
import os
import hashlib
from glob import glob

def table_exists(table_name, connection):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None


def drop_tables(conn, table_names):
    cursor = conn.cursor()

    # Disable foreign key constraints temporarily if needed.
    cursor.execute("PRAGMA foreign_keys = OFF;")

    for table in table_names:
        cursor.execute(f"DROP TABLE IF EXISTS {table};")
        print(f"Table {table} dropped (if it existed).")

    # Re-enable foreign key constraints.
    cursor.execute("PRAGMA foreign_keys = ON;")

    conn.commit()

# sanitizes whole column of dataframe
def sanitize_price_column(price):
    cleaned_price = price.str.replace(r'[\$,]', '', regex=True)
    return (cleaned_price.astype(float) * 100).astype(int)


def init_db():
    db_path = "..//database.db"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL
            );
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Helpdesk (
            email TEXT PRIMARY KEY,
            Position TEXT NOT NULL
            );
        """)

    # status is an int, so handle non 0/1 vals in API
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Requests (
            request_id INTEGER PRIMARY KEY,
            sender_email TEXT NOT NULL,
            helpdesk_staff_email TEXT NOT NULL,
            request_type TEXT NOT NULL,
            request_desc TEXT NOT NULL,
            request_status INTEGER NOT NULL
            );
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Buyers (
            email TEXT PRIMARY KEY,
            business_name TEXT NOT NULL,
            buyer_address_id TEXT NOT NULL,
            FOREIGN KEY(email) REFERENCES Users(email),
            FOREIGN KEY(buyer_address_id) REFERENCES Address(address_id)
            );
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Credit_Cards (
            credit_card_num TEXT PRIMARY KEY,
            card_type TEXT NOT NULL,
            expire_month INTEGER NOT NULL,
            expire_year INTEGER NOT NULL,
            security_code INTEGER NOT NULL,
            owner_email TEXT NOT NULL,
            FOREIGN KEY(owner_email) REFERENCES Buyers(email)
            );
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Address (
            address_id TEXT PRIMARY KEY,
            zipcode INTEGER NOT NULL,
            street_num INTEGER NOT NULL,
            street_name TEXT NOT NULL
            );
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Zipcode_Info (
            zipcode INTEGER PRIMARY KEY,
            city TEXT NOT NULL,
            state TEXT NOT NULL
            );
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Sellers (
            email TEXT PRIMARY KEY,
            business_name TEXT NOT NULL,
            business_address_id TEXT NOT NULL,
            bank_routing_number INTEGER NOT NULL,
            bank_account_number INTEGER NOT NULL,
            balance REAL NOT NULL,
            FOREIGN KEY(email) REFERENCES Users(email),
            FOREIGN KEY(business_address_id) REFERENCES Address(address_id)
            );
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Categories (
            category_name TEXT PRIMARY KEY,
            parent_category TEXT
            );
        """)

    # status codes: 1-active, 0-inactive, 2-sold ; default value is 1
    # UPON INSERTION, IF LISTING_ID IS NULL SET TO INCREMENT
    # product price is price*100 and type integer
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Product_Listings (
            seller_email TEXT,
            listing_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            product_title TEXT NOT NULL,
            product_name TEXT NOT NULL,
            product_description TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            product_price INTEGER NOT NULL,
            status INTEGER NOT NULL,
            PRIMARY KEY(listing_id, seller_email)
            );
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Orders (
            order_id integer PRIMARY KEY,
            seller_email TEXT NOT NULL,
            listing_id INTEGER NOT NULL,
            buyer_email TEXT NOT NULL,
            date TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            payment REAL NOT NULL,
            FOREIGN KEY(buyer_email) REFERENCES Users(email),
            FOREIGN KEY(listing_id, seller_email) REFERENCES Product_Listings(listing_id, seller_email)
            );
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Reviews (
            order_id INTEGER PRIMARY KEY,
            review_desc TEXT NOT NULL,
            rate INTEGER NOT NULL,
            FOREIGN KEY(order_id) REFERENCES Orders(order_id)
            );
        """)

    static_backup = ".\\static_backup\\"
    csv_files = glob(os.path.join(static_backup, "*.csv"))

    print(f"Found {len(csv_files)} CSV files(s) in {static_backup}.......................")

    for file in csv_files:
        print(f"Processing {file}")
        df = pd.read_csv(file)

        table_name = os.path.splitext(os.path.basename(file))[0]

        # if table_exists(table_name, connection):
        #     print(f"Table {table_name} already exists, skipping....")
        #     continue

        if table_name == "Users":
            #dev team agrees on SHA 256 hashing
            df['password'] = df['password'].apply(lambda pwd: hashlib.sha256(pwd.encode('utf-8)')).hexdigest())
        if table_name == "Product_Listings":
            df['Product_Price'] = sanitize_price_column(df['Product_Price'])
        # else:
        #     continue

        try:
            df.columns = df.columns.str.strip()
            df.to_sql(table_name, connection, if_exists='append', index=False)
            print(f"Inserted data into table '{table_name}'.")
        except Exception as e:
            print(f"Skipping {file}: {e}")
            pass


    connection.commit()
    connection.close()
    print("Database initialized.")

if __name__ == '__main__':

    tables_to_drop = [
        'Users',
        'helpdesk',
        'requests',
        'buyers',
        'credit_cards',
        'address',
        'zipcode_info',
        'sellers',
        'categories',
        'product_listings',
        'orders',
        'Reviews'
    ]
    db_path = "..//database.db"
    connection = sqlite3.connect(db_path)
    #table dropping on startup is for testing purposes - remove in production
    #drop_tables(connection, tables_to_drop)

    init_db()