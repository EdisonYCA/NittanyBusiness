from app.helpdesk import bp
from flask import render_template
import sqlite3 as sql
#if the db doesn't work tell richie
from app import get_db

@bp.route('/')
def index():
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Requests;')
    result = cursor.fetchall()
    return render_template('helpdesk/index.html', result=result)