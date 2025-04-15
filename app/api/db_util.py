import pandas as pd
import sqlite3
import os
import hashlib
import sys
from glob import glob
from flask import g
from config import Config

DB_PATH = Config.DB_PATH

# will create db from backup if db is not found.
def get_db():
    if 'db' not in g:
        if not os.path.exists(DB_PATH):
            script_path = os.path.join(os.path.dirname(__file__), '..', 'db_utils', 'db_init.py')
            try:
                init_db()
                # subprocess.run(['python', script_path], check=True)
            except Exception as e:
                print(f"Failed to run population script: {e}")
                raise
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


# sanitizes whole column of dataframe
def sanitize_price_column(price):
    cleaned_price = price.str.replace(r'[\$,]', '', regex=True)
    return (cleaned_price.astype(float) * 100).astype(int)


def init_db():
    # db path can be pointed to config, but db_utils will need to be integrated into modules.
    db_path = Config.DB_PATH
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

    csv_files = glob(os.path.join(Config.STATIC_BACKUP_PATH, '*.csv'))
    print(f"Found {len(csv_files)} CSV file(s) in {Config.STATIC_BACKUP_PATH}...")

    for file in csv_files:
        print(f"Processing {file}")
        df = pd.read_csv(file)

        table_name = os.path.splitext(os.path.basename(file))[0]

        # if table_exists(table_name, connection):
        #     print(f"Table {table_name} already exists, skipping....")
        #     continue

        if table_name == "Users":
            # dev team agrees on SHA 256 hashing
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