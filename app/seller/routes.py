from app.seller import bp
from flask import render_template, redirect, url_for


@bp.route('/')
def index():
    return redirect(url_for('api.get_seller_products'))

@bp.route('/publish')
def publish():
    return render_template("seller/product_form.html")


