from app.main import bp
from flask import render_template
#if the db doesn't work tell richie
from app import get_db

@bp.route('/')
def index():
    return render_template('index.html')