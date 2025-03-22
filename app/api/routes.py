from flask import request
from app import get_db
from app.api import bp


# login checks if email and password match any row in the database
@bp.route("/users", methods=["POST"])
def login():
    """
    Expects JSON: { "email": "...", "password": "..." }
    """

    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return f"Email: {email}, Password: {password} is invalid"

    db = get_db()
    user = db.execute("SELECT * FROM Users WHERE email = ?", [email]).fetchone()

    if user is None or user["password"] != password:
        return f"Email: {email}, Password: {password}, user: {user} is invalid because password doesn't match"
    #
    return f"Received form data! Email: {email}, Password: {password}"
