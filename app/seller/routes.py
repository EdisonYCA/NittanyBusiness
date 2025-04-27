from app.seller import bp
from flask import render_template, redirect, url_for, session
import sqlite3
from app import get_db


@bp.route('/')
def index():
    return redirect(url_for('api.get_seller_products'))

@bp.route('/publish')
def publish():
    return render_template("seller/product_form.html")


@bp.route('/change_product_form/<int:listing_id>',methods=['GET'], endpoint='change_product_form')
def change_product_form(listing_id):
    seller_email = session.get('user')
    if not seller_email:
        return redirect(url_for('login.index'))

    db = get_db()
    db.row_factory = sqlite3.Row
    product = db.execute("SELECT * FROM Product_Listings WHERE seller_email = ? AND listing_id = ?",(seller_email, listing_id)).fetchone()

    if product is None:
        return "Product not found", 404

    return render_template('seller/change_product_form.html', product=product)
