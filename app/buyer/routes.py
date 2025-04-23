from app.buyer import bp
from flask import render_template, request
from app.utils.auth import login_required
import sqlite3
from app import get_db


@bp.route('/')
@login_required
def index():
    return render_template('buyer/index.html')

@bp.route('/search', methods=['POST'])
def search():
    search_val = request.form.get('search')
    search_val_query = "%" + search_val + "%"

    db = get_db()
    cursor = db.cursor()

    try:
        rows = cursor.execute("""SELECT *
                                 from Product_Listings
                                 join Sellers
                                 on seller_email = email
                                 where (category LIKE ?) or (product_title LIKE ?) or (product_description LIKE ?) or (business_name = ?)
                              """,(search_val_query, search_val_query, search_val_query, search_val_query)).fetchall()
    except Exception as e:
        print(e)
        return f'Error: {e}'
    finally:
        db.close()

    result = [dict(row) for row in rows]
    return render_template('buyer/search.html', search=search_val, results=result)