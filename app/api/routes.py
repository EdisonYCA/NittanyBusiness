from flask import request, redirect, url_for
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
