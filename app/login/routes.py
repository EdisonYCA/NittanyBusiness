from flask import render_template
from app.login import bp
#if the db doesn't work tell richie
from app import get_db

@bp.route('/')
def index():
    return render_template('login/index.html')