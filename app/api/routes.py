import sqlite3

from click import confirm
from flask import request, redirect, url_for, render_template, jsonify, session
from app import get_db
from app.api import bp
import hashlib
import re


def hash_password(password):
    if not password:
        return ""

    sha256 = hashlib.new("SHA256")
    sha256.update(password.encode())
    hashed_password = sha256.hexdigest()
    return hashed_password


def validate_email(email):
    if not email:
        return False

    regex = re.compile("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return regex.match(email) is not None


# this endpoint sets a request to inactive
@bp.route('/complete_request', methods=['POST'])
def complete_requests():
    req_id = request.form.get("request_id")

    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # status 0 is incomplete, 1 is complete - id must be passed as 1 element tuple
    try:
        cursor.execute("UPDATE requests SET request_status = 1 WHERE request_id = ?", (req_id,))
        db.commit()
    finally:
        db.close()

    return f"Request #{req_id} marked complete"


# this grabs the requests for the helpdesk
@bp.route('/get_active_requests', methods=['POST'])
def get_active_requests():
    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # status 0 is incomplete, 1 is complete
    cursor.execute("SELECT * FROM requests WHERE request_status = 0")
    rows = cursor.fetchall()
    requests = [dict(row) for row in rows]
    db.close()

    return jsonify(requests)


# login checks if email and password match any row in the database
@bp.route("/users", methods=["POST"])
def login():
    emailS = request.form.get("email")
    password = hash_password(request.form.get("password"))

    if not validate_email(emailS) or not password:
        return redirect(url_for("login.index", login_failed=True))

    db = get_db()
    user = db.execute("SELECT * FROM Users WHERE email = ?", [emailS]).fetchone()

    if user is None or user["password"] != password:
        return redirect(url_for("login.index", login_failed=True))

    return f"Successful Login!"


# Signup route for new user registration
@bp.route("/signup", methods=["POST"])
def signup():
    newEmail = request.form.get("email")
    newPassword = request.form.get("password")
    confirmPassword = request.form.get("passwordConf")
    accountType = request.form.get("accountType")
    businessName = request.form.get("businessName")

    if not validate_email(newEmail) or not newPassword or not confirmPassword:
        return redirect(url_for("signup.index", signup_failed=True))

    # Match passwords
    if newPassword != confirmPassword:
        return redirect(url_for("signup.index", password_match_failed=True))

    if len(newPassword) < 8 or not any(char.isupper() for char in newPassword):
        return redirect(url_for("signup.index", password_requirements=True))

    db = get_db()

    try:
        # Check if the email already exists
        existing_user = db.execute("SELECT * FROM Users WHERE email = ?", [newEmail]).fetchone()
        if existing_user is not None:
            return redirect(url_for("signup.index", signup_exists=True))

        # Insert the new user into the Users table
        hashed_password = hash_password(newPassword)
        db.execute("INSERT INTO Users (email, password) VALUES (?, ?)", [newEmail, hashed_password])
        db.commit()

        # Insert into the relevant table based on the account type
        if accountType == "seller":
            return render_template("signup/seller.html", email=newEmail, businessName=businessName)
        elif accountType == "buyer":
            return render_template("signup/buyer.html", email=newEmail, businessName=businessName)
        else:
            return redirect(url_for("signup.index", signup_failed=True))

    except Exception as e:
        print(f"Database Error: {e}")
        return redirect(url_for("signup.index", signup_failed=True))

@bp.route('/signupSeller', methods=['POST'])
def signupSeller():
    email = session.get('email')  # Retrieve the email stored in the session
    street_num = request.form.get('street_num')
    street_name = request.form.get('street_name')
    zipcode = request.form.get('zipcode')
    city = request.form.get('city')
    state = request.form.get('state')
    bank_routing_number = request.form.get('bank_routing_number')
    bank_account_number = request.form.get('bank_account_number')

    db = get_db()
    try:
        # Insert Address and Zipcode_Info
        address_id = f"{street_num}_{street_name}_{zipcode}"  # Generate address ID
        db.execute("INSERT INTO Address (address_id, street_num, street_name, zipcode) VALUES (?, ?, ?, ?)",
                   [address_id, street_num, street_name, zipcode])
        db.execute("INSERT INTO Zipcode_Info (zipcode, city, state) VALUES (?, ?, ?)",
                   [zipcode, city, state])

        # Insert Seller Information
        db.execute("""
                INSERT INTO Sellers (email, business_name, business_address_id, bank_routing_number, bank_account_number, balance)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [email, session.get('businessName'), address_id, bank_routing_number, bank_account_number, 0.0])

        db.commit()
        return redirect(url_for("profile.index", success=True))  # Redirect to a success page
    except Exception as e:
        print(f"Seller Details Error: {e}")
        return redirect(url_for("profile.index", profile_failed=True))  # Redirect in case of failure



@bp.route('/signupBuyer', methods=['POST'])
def signupBuyer():
        email = session.get('email')
        street_num = request.form.get('street_num')
        street_name = request.form.get('street_name')
        zipcode = request.form.get('zipcode')
        city = request.form.get('city')
        state = request.form.get('state')
        credit_card_num = request.form.get('credit_card_num')
        card_type = request.form.get('card_type')
        expire_month = request.form.get('expire_month')
        expire_year = request.form.get('expire_year')
        security_code = request.form.get('security_code')

        db = get_db()
        try:
            # Insert Address and Zipcode_Info
            address_id = f"{street_num}_{street_name}_{zipcode}"
            db.execute("INSERT INTO Address (address_id, street_num, street_name, zipcode) VALUES (?, ?, ?, ?)",
                       [address_id, street_num, street_name, zipcode])
            db.execute("INSERT INTO Zipcode_Info (zipcode, city, state) VALUES (?, ?, ?)", [zipcode, city, state])

            # Insert Buyer and Credit Card
            db.execute("INSERT INTO Buyers (email, business_name, buyer_address_id) VALUES (?, ?, ?)",
                       [email, session.get('businessName'), address_id])
            db.execute("""
                INSERT INTO Credit_Cards (credit_card_num, card_type, expire_month, expire_year, security_code, owner_email)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [credit_card_num, card_type, expire_month, expire_year, security_code, email])

            db.commit()
            return redirect(url_for("profile.index", success=True))  # Redirect to a success page
        except Exception as e:
            print(f"Buyer Details Error: {e}")
            return redirect(url_for("profile.index", profile_failed=True))  # Redirect in case of failure
