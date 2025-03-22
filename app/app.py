from flask import Flask, request, render_template, redirect, url_for, flash
import sqlite3 as sql
import hashlib
import csv
app = Flask(__name__)
app.secret_key = "your_secret_key"
host = 'http://127.0.0.1:5000/'

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'



def hashing_password(password):
    #hashing algorithm to change this password into hashed password
    hash = hashlib.new("SHA256")
    hash.update(password.encode())
    passwordHash = hash.hexdigest()
    return passwordHash


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        #check if password and email is in the database
        hashPassword = hashing_password(password)
        connection = sql.connect("NittanyBusiness.db")
        cursor = connection.cursor()
        cursor = connection.execute("SELECT email, password FROM users WHERE email = ? and hashed_password = ?", (email,hashPassword))
        user = cursor.fetchone()
        connection.close()
        #have to check if user is a buyer or seller
        if user:
            flash("Logged in!", "success")
            return redirect(url_for('homeBuyer'))
        else:
            flash("Invalid email or password!", "danger")
    #return login page, here I said login html but idk the actual html page
    return render_template('login.html')


#home page
@app.route("/homeBuyer")
def homeBuyer():
    return "Welcome back to the Buyer Home Page!"

@app.route("/homeSeller")
def homeBuyer():
    return "Welcome back to the Seller Home Page!"

if __name__ == '__main__':
    app.run()
