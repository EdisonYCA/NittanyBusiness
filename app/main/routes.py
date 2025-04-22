from app.main import bp
from flask import render_template, session
#if the db doesn't work tell richie
from app import get_db

@bp.route('/')
def index():
    active = 'user' in session
    return render_template('index.html', active=active)