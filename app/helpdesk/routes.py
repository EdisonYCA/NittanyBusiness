from app.helpdesk import bp
from app import get_db
from flask import render_template
import sqlite3

@bp.route('/')
def index():
    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # status 0 is incomplete, 1 is complete
    cursor.execute("SELECT * FROM requests WHERE request_status = 0")
    rows = cursor.fetchall()
    db.close()

    return render_template('helpdesk/index.html', result=rows)

@bp.route('/claim')
def claim():
    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # status 0 is incomplete, 1 is complete
    cursor.execute("SELECT * FROM requests WHERE (request_status = 0) & (helpdesk_staff_email = 'helpdeskteam@nittybiz.com')")
    rows = cursor.fetchall()
    db.close()

    return render_template('helpdesk/claim.html', result=rows)

@bp.route('/view')
def view():
    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # status 0 is incomplete, 1 is complete
    cursor.execute("SELECT * FROM requests WHERE request_status = 0")
    rows = cursor.fetchall()
    db.close()

    return render_template('helpdesk/view.html', result=rows)

@bp.route('/addcategory')
def addcategory():
    return render_template('helpdesk/addcategory.html')