from flask import render_template, request, session, redirect, url_for, flash
from app.login import bp
from app.utils import auth
from app.utils import db as db_utils
from app import get_db


@bp.route('/')
def index():
    failed = request.args.get("login_failed", False)
    return render_template('login/index.html', login_failed=failed)


@bp.route("/users", methods=["POST"])
def login():
    emailS = request.form.get("email")
    password = auth.hash_password(request.form.get("password"))

    if not auth.validate_email(emailS) or not password:
        return redirect(url_for("login.index", login_failed=True))

    db = get_db()
    user = db.execute("SELECT * FROM Users WHERE email = ?", [emailS]).fetchone()

    if user is None or user["password"] != password:
        return redirect(url_for("login.index", login_failed=True))

    user_type = db_utils.get_user_type(emailS)
    session["user"] = emailS
    session["user_type"] = user_type

    if user_type == "Buyer":
        return render_template("buyer/index.html")
    elif user_type == "Seller":
        return render_template("seller/index.html")
    else:
        return render_template("helpdesk/index.html")

    return redirect(url_for("login.index", login_failed=True))