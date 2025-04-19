from app.checkout import bp
from app import get_db
from flask import render_template
import sqlite3

@bp.route('/', methods=['POST'])
def index():
    return render_template('checkout/index.html')
