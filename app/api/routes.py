from click import confirm
from flask import request, redirect, url_for, render_template
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


# login checks if email and password match any row in the database
@bp.route("/users", methods=["POST"])
def login():
    email = request.form.get("email")
    password = hash_password(request.form.get("password"))

    if not validate_email(email) or not password:
        return redirect(url_for("login.index", login_failed=True))

    db = get_db()
    user = db.execute("SELECT * FROM Users WHERE email = ?", [email]).fetchone()

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
        return redirect(url_for("signup.index", signup_failed=True))
    #match password
    if newPassword != confirmPassowrd:
        return redirect(url_for("signup.index", password_match_faile=True))

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
            return render_template("signup/buyer.html", email=newEmail)
        else:
            return redirect(url_for("signup.index", signup_failed=True))


    except Exception as e:
        print(f"Database Error: {e}")
        return redirect(url_for("signup.index", signup_failed=True))