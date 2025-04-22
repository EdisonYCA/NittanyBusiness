from flask import render_template
from app.signup import bp

@bp.route('/')
def index():
    return render_template('signup/index.html')