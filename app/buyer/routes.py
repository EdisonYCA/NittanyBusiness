from app.buyer import bp
from flask import render_template, request, make_response, jsonify, session
from app.utils.auth import login_required
import sqlite3
from app import get_db


@bp.route('/')
@login_required
def index():
    parent_category = request.form.get('parent_category')

    if parent_category is None:
        db = get_db()
        db.row_factory = sqlite3.Row
        cursor = db.cursor()

        # status 0 is incomplete, 1 is complete - id must be passed as 1 element tuple
        cursor.execute("SELECT * FROM categories WHERE parent_category = 'Root'")
        rows = cursor.fetchall()
        db.close()

        # return render_template('standin_name/some_page.html', result=rows)

        # this return is just for testing with test script
        result = [dict(row) for row in rows]
        return render_template('buyer/index.html', result=result)

    return render_template("buyer/index.html")


@bp.route('/search', methods=['POST'])
def search():
    search_val = request.form.get('search')
    search_val_query = "%" + search_val + "%"
    min_cost_range = request.form.get('minCostRange')
    max_cost_range = request.form.get('maxCostRange')

    # If nothing was entered, search returns no products
    if search_val is "":
        return render_template('buyer/search.html', search=search_val, result=None)

    db = get_db()
    cursor = db.cursor()

    try:
        rows = cursor.execute("""SELECT *
                                 from Product_Listings
                                 join Sellers
                                 on seller_email = email
                                 where ((category LIKE ?) or (product_title LIKE ?) or (product_description LIKE ?) or (business_name = ?)) and (product_price >= ? and product_price <= ?) and (quantity != 0)
                              """,(search_val_query, search_val_query, search_val_query, search_val_query, min_cost_range, max_cost_range)).fetchall()
    except Exception as e:
        print(e)
        return f'Error: {e}'
    finally:
        db.close()

    result = [dict(row) for row in rows]
    return render_template('buyer/search.html', search=search_val, results=result)

@bp.route('/get_sub_cat', methods=['POST'])
def get_sub_cat():
    req = request.get_json()
    parent_category = req['parent']

    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # status 0 is incomplete, 1 is complete - id must be passed as 1 element tuple
    cursor.execute("SELECT * FROM categories WHERE parent_category = ?", (parent_category,))
    rows = cursor.fetchall()
    db.close()

    result = [dict(row) for row in rows]
    #print(result)

    res = make_response(jsonify(result), 200)

    return res