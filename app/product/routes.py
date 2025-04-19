from flask import render_template
from app.product import bp

@bp.route('/')
def product():
    return render_template('product/index.html')