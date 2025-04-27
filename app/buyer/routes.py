from app.buyer import bp
from flask import render_template, request, make_response, jsonify, session, redirect, url_for
from app.utils.auth import login_required
from app.utils.auth import hash_password
import sqlite3
import random
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

@bp.route('get_setting')
def get_setting():
    user = session.get('user')

    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    cursor.execute("""SELECT BUYERS.email, BUYERS.business_name,
                        CREDIT_CARDS.credit_card_num, CREDIT_CARDS.card_type, CREDIT_CARDS.expire_month, CREDIT_CARDS.expire_year, CREDIT_CARDS.security_code,
                        ADDRESS.address_id, ADDRESS.zipcode, ADDRESS.street_num, ADDRESS.street_name from Buyers
                        JOIN USERS on Buyers.email = USERS.email
                        JOIN Credit_Cards on Buyers.email = Credit_Cards.owner_email
                        JOIN ADDRESS on Buyers.buyer_address_id = ADDRESS.address_id
                        WHERE BUYERS.email = ?""", (user,))
    rows = cursor.fetchall()
    db.close()

    ret = [dict(row) for row in rows]

    #print(ret)
    return render_template('buyer/setting.html', result=ret)

@bp.route('update_setting', methods=["POST"])
def update_setting():
    user = session.get('user')
    business_name = request.form.get('business_name')
    credit_card_num = request.form.get('credit_num')
    expire_date = request.form.get('expire_date')
    expire_date_parse = expire_date.split('/')
    security_code = request.form.get('security_code')
    zipcode = request.form.get('zip_code')
    street_name = request.form.get('street_name')
    street_num = request.form.get('street_num')
    address_id = request.form.get('address_id')
    password = request.form.get('password')
    conf_password = request.form.get('conf_password')

    print(address_id, zipcode, street_name, street_num)

    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    #cursor.execute("UPDATE Sellers set balance = balance + ? where email = ?", [price, seller_email])
    cursor.execute("UPDATE BUYERS SET business_name = ? where email = ?",
                   [business_name, user])

    cursor.execute("UPDATE Credit_Cards SET credit_card_num = ? where owner_email = ?",
                   [credit_card_num, user])
    cursor.execute("UPDATE Credit_Cards SET expire_month = ? where owner_email = ?",
                   [int(expire_date_parse[0]), user])
    cursor.execute("UPDATE Credit_Cards SET expire_year = ? where owner_email = ?",
                   [int(expire_date_parse[1]), user])
    cursor.execute("UPDATE Credit_Cards SET security_code = ? where owner_email = ?",
                   [security_code, user])

    cursor.execute("UPDATE Address SET zipcode = ? where address_id = ?",
                   [int(zipcode), address_id])
    cursor.execute("UPDATE Address SET street_name = ? where address_id = ?",
                   [street_name, address_id])
    cursor.execute("UPDATE Address SET street_num = ? where address_id = ?",
                   [int(street_num), address_id])
    db.commit()

    if password == conf_password:
        password = hash_password(password)
        cursor.execute("UPDATE USERS SET password = ? where email = ?",
                       [password, user])
        db.commit()
        db.close()
    else:
        db.close()
        return redirect(url_for('buyer.get_setting'))

    return redirect(url_for('buyer.get_setting'))

@bp.route('update_email', methods=["POST"])
def update_email():
    new_email = request.form.get('new_email')
    user = session.get('user')

    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    cursor.execute("INSERT INTO Requests (request_id, sender_email, helpdesk_staff_email, request_type, request_desc, request_status) VALUES (?, ?, ?, ?, ?, ?)",
                   [random.randint(1, 100000000), user, 'helpdeskteam@nittybiz.com', 'ChangeID', 'Please change my ID to ' + new_email, 0])
    db.commit()
    db.close()
    return redirect(url_for('buyer.get_setting'))