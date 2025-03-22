from urllib import request
from flask import jsonify
from flask import Blueprint

from flask import Blueprint
from app import get_db

#login checks if username and password match any row in the database
@api_bp.route("/users", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Missing username and password"}), 400

    username = data["username"]
    password = data["password"]

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", [username]).fetchone()

    if user is None or user["password"] != password:
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"message": "Logged in successfully"}), 200
