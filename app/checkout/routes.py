from app.checkout import bp
from app import get_db
from flask import render_template, session, jsonify, make_response
import sqlite3

@bp.route('/', methods=['POST'])
def index():
    return render_template('checkout/index.html')

@bp.route('/get_credit', methods=['GET', 'POST'])
def get_credit():
    email = session.get('user')

    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # status 0 is incomplete, 1 is complete - id must be passed as 1 element tuple
    cursor.execute("SELECT * FROM Credit_Cards WHERE owner_email = ?", (email,))
    rows = cursor.fetchall()
    db.close()

    result = [dict(row) for row in rows]

    res = make_response(jsonify(result), 200)

    return res

@bp.route('/rate', methods=['GET', 'POST'])
def rate():
    return render_template('checkout/rate.html', product_name = "test")