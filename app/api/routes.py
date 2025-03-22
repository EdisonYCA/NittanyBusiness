from flask import request
from flask import jsonify
from flask import Blueprint
from app import get_db

api_bp = Blueprint('api_bp', __name__)

#login checks if email and password match any row in the database
@api_bp.route("/users", methods=["POST"])
def login():
    """
    Expects JSON: { "email": "...", "password": "..." }
    """

    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing email and password"}), 400

    email = data["email"]
    password = data["password"]

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", [email]).fetchone()

    if user is None or user["password"] != password:
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"message": "Logged in successfully"}), 200
