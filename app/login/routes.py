from flask import render_template
from app.login import bp
from flask import request
from flask import jsonify
# if the db doesn't work tell richie
from app import get_db
import hashlib


def hashing_password(password):
    # hashing algorithm to change this password into hashed password
    sha256 = hashlib.new("SHA256")
    sha256.update(password.encode())
    hashed_password = sha256.hexdigest()
    return hashed_password


@bp.route('/')
def index():
    return render_template('login/index.html')
