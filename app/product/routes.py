from flask import render_template
from app.product import bp

@bp.route('/')
def index():
    return render_template('product/index.html')