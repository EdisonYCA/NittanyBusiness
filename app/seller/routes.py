from app.seller import bp
from flask import render_template


@bp.route('/')
def index():
    return render_template('seller/index.html')
