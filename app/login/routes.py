from flask import render_template
from app.login import bp

@bp.route('/')
def index():
    return render_template('login/index.html')