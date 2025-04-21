import sqlite3

from click import confirm
from flask import request, redirect, url_for, render_template, jsonify
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


def get_prod_id(email):
    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    row = cursor.execute("SELECT MAX(listing_id) FROM Product_Listings WHERE seller_email = ?", (email,)).fetchone()
    if row[0] is None:
        row = cursor.execute("SELECT * FROM Sellers WHERE email = ?", (email,)).fetchone()
        if row[0] is None:
            raise Exception("Invalid email")
        else:
            return 1
    return row[0] + 1


#this endpoint grabs the children of whatever category was passed in
@bp.route('/child_categories', methods=['POST'])
def get_child_categories():

    parent_category = request.form.get("category")

    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # status 0 is incomplete, 1 is complete - id must be passed as 1 element tuple
    cursor.execute("SELECT * FROM categories WHERE parent_category = ?", (parent_category,))
    rows = cursor.fetchall()
    db.close()

    # return render_template('standin_name/some_page.html', result=rows)

    #this return is just for testing with test script
    result = [dict(row) for row in rows]
    return jsonify(result)


#takes in product specs and creates new product listing
@bp.route('/add_product', methods=['POST'])
def add_product():

    seller_id = request.form.get("seller_id")
    # product_id = request.form.get("product_id")
    category = request.form.get("category")
    product_name = request.form.get("product_name")
    quantity = request.form.get("quantity")
    price = request.form.get("price")
    status = request.form.get("status")
    product_description = request.form.get("product_description")
    product_title = request.form.get("product_title")
    try:
        product_id = get_prod_id(seller_id)
    except Exception as e:
        return f"error during product_id creation: {e}"

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("INSERT into Product_Listings (seller_email, listing_id, category, product_title, product_name, product_description, quantity, product_price, status) VALUES (?,?,?,?,?,?,?,?,?)",
                   [seller_id, product_id, category, product_title, product_name, product_description, quantity, price, status])
        db.commit()
    except sqlite3.IntegrityError as e:
        print(e)
        return f"Error: {e}"
    return f"Product {product_id} added to listing {seller_id}"


# this endpoint grabs top level categories
@bp.route('/top_level_categories', methods=['POST'])
def get_top_level_categories():

    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # status 0 is incomplete, 1 is complete - id must be passed as 1 element tuple
    cursor.execute("SELECT * FROM categories WHERE parent_category = 'Root'")
    rows = cursor.fetchall()
    db.close()

    # return render_template('standin_name/some_page.html', result=rows)

    #this return is just for testing with test script
    result = [dict(row) for row in rows]
    return jsonify(result)


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

    return redirect(url_for('helpdesk.index'))
     # return f"Request #{req_id} marked complete"


# this grabs the requests for the helpdesk
@bp.route('/get_active_requests')
def get_active_requests():
    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # status 0 is incomplete, 1 is complete
    cursor.execute("SELECT * FROM requests WHERE request_status = 0")
    rows = cursor.fetchall()
    db.close()

    return render_template('helpdesk/index.html', result=rows)


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
    confirmPassowrd = request.form.get("passwordConf")
    accountType = request.form.get("accountType")

    if not validate_email(newEmail) or not newPassword or not confirmPassowrd:
    #if not newPassword or not confirmPassowrd:
        return redirect(url_for("signup.index", signup_failed=True))
    #match password
    if newPassword != confirmPassowrd:
        return redirect(url_for("signup.index", password_match_failed=True))

    if len(newPassword) < 8 or not any(char.isupper() for char in newPassword):
        return redirect(url_for("signup.index", password_requirements=True))

    db = get_db()

    try:
        # Check if the email already exists
        existing_user = db.execute("SELECT * FROM Users WHERE email = ?", [newEmail]).fetchone()
        if existing_user is not None:
            return redirect(url_for("signup.index", signup_exists=True))

        # Insert new user into the database
        hashed_password = hash_password(newPassword)
        db.execute("INSERT INTO Users (email, password) VALUES (?, ?)", [newEmail, hashed_password])
        db.commit()

        # Render different templates based on accountType
        if accountType == "seller":
            return render_template("signup/seller.html", email=newEmail)
        elif accountType == "buyer":
            return render_template("profile/buyerProfile.html", email=newEmail)
        else:
            return redirect(url_for("signup.index", signup_failed=True))


    except Exception as e:
        print(f"Database Error: {e}")
        return redirect(url_for("signup.index", signup_failed=True))


