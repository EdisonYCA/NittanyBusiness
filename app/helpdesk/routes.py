from app.helpdesk import bp
from app import get_db
from flask import render_template, request, session, redirect, url_for
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

@bp.route('/claim_request', methods=['POST'])
def claim_request():
    request_id = request.form.get('request_id')
    user = session.get('user')

    db = get_db()
    cursor = db.cursor()

    cursor.execute("UPDATE requests SET helpdesk_staff_email = ? where request_id = ?", (user, request_id))
    db.commit()
    db.close()
    return redirect(url_for("helpdesk.claim"))

@bp.route('/view')
def view():
    user = session.get('user')
    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # status 0 is incomplete, 1 is complete
    cursor.execute("SELECT * FROM requests WHERE request_status = 0 and helpdesk_staff_email = ?", (user,))
    rows = cursor.fetchall()
    db.close()

    return render_template('helpdesk/view.html', result=rows)

@bp.route('/addcategory')
def addcategory():
    return render_template('helpdesk/addcategory.html')

@bp.route('/addcatfunc', methods=['POST'])
def addcatfunc():
    cat_name = request.form.get("category_name")
    parent_name = request.form.get("parent_category_name")

    db = get_db()
    cursor = db.cursor()

    try:
        row = cursor.execute("SELECT * FROM Categories WHERE category_name = ?", (cat_name,)).fetchall()
        if len(row) == 0:
            cursor.execute("INSERT into Categories (category_name, parent_category) VALUES (?, ?)", (cat_name, parent_name))
            db.commit()
        else:
            return render_template('helpdesk/addcategory.html', ret='fail')
    except Exception as e:
        print(f"Database Error: {e}")
        return f"Error while inserting new category: {e}"
    finally:
        db.close()
    return render_template('helpdesk/addcategory.html', ret='success')