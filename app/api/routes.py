import sqlite3

from click import confirm
from flask import request, redirect, url_for, render_template, jsonify, session
from app import get_db
from app.api import bp
from datetime import datetime
import hashlib
import re


def hash_password(password):
    if not password:
        return ""

    sha256 = hashlib.new("SHA256")
    sha256.update(password.encode())
    hashed_password = sha256.hexdigest()
    return hashed_password


def validate_email(email):
    if not email:
        return False

    regex = re.compile("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return regex.match(email) is not None


# calculates incremented product_id per requirements analysis
def get_prod_id(email):
    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    row = cursor.execute("SELECT MAX(listing_id) FROM Product_Listings WHERE seller_email = ?", (email,)).fetchone()
    if row[0] is None:
        row = cursor.execute("SELECT * FROM Sellers WHERE email = ?", (email,)).fetchone()
        if row[0] is None:
            raise Exception("Invalid email")
        else:
            return 1
    return row[0] + 1


# checks if user is a buyer, seller, or helpdesk user
def get_user_type(email):
    db = get_db()
    buyer = db.execute("SELECT * FROM Buyers WHERE email = ?", [email]).fetchone()
    seller = db.execute("SELECT * FROM Sellers WHERE email = ?", [email]).fetchone()

    if buyer:
        return "Buyer"
    if seller:
        return "Seller"
    return "Helpdesk"


#gets product info so that front end can leave some fields blank on update
def update_listing(seller_email, listing_id,*,category=None,product_title=None,product_name=None, product_description=None,status=None,quantity=None,product_price=None):

    to_update = {}
    if category is not None: to_update['category'] = category
    if product_title is not None: to_update['product_title'] = product_title
    if product_name is not None: to_update['product_name'] = product_name
    if product_description is not None: to_update['product_description'] = product_description
    if status is not None: to_update['status'] = status
    if quantity is not None: to_update['quantity'] = quantity
    if product_price is not None: to_update['product_price'] = product_price

    # print(f"[DEBUG] update_listing(): fields to update = {to_update}")

    if not to_update:
        return False

    cols = ", ".join(f"{col}=?" for col in to_update)
    params = list(to_update.values()) + [seller_email, listing_id]
    sql = f"UPDATE Product_Listings SET {cols} WHERE seller_email = ? AND listing_id = ?"

    db = get_db()
    cursor = db.execute(sql, params)
    rowcount = cursor.rowcount
    db.commit()

    # print(f"[DEBUG] Executed SQL: {sql}")

    return rowcount


# gets all products by category
@bp.route("/prod_by_cat", methods=["POST"])
def prod_by_cat():
    category = request.form.get("category")

    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    try:
        cursor.execute("SELECT * FROM Product_Listings, Sellers WHERE category = ? and Product_listings.seller_email = Sellers.email", (category,))
        rows = cursor.fetchall()
        db.close()
    except Exception as e:
        print(e)
        return f'Error: {e}'

    result = [dict(row) for row in rows]
    return render_template('buyer/prodByCat.html', result=result, category=category)
    #return jsonify(result)


# gets all products by seller
@bp.route("/prod_by_seller", methods=["POST"])
def prod_by_seller():
    seller_id = request.form.get("seller_id")

    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    try:
        cursor.execute("SELECT * FROM Product_Listings WHERE seller_email = ?", (seller_id,))
        rows = cursor.fetchall()
        db.close()
    except Exception as e:
        print(e)
        return f'Error: {e}'

    result = [dict(row) for row in rows]
    return jsonify(result)


# this endpoint grabs the children of whatever category was passed in
@bp.route('/child_categories', methods=['POST'])
def get_child_categories():
    parent_category = request.form.get("category")

    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # status 0 is incomplete, 1 is complete - id must be passed as 1 element tuple
    cursor.execute("SELECT * FROM categories WHERE parent_category = ?", (parent_category,))
    rows = cursor.fetchall()
    db.close()

    # return render_template('standin_name/some_page.html', result=rows)

    # this return is just for testing with test script
    result = [dict(row) for row in rows]
    return jsonify(result)


#takes in product specs and creates new product listing
@bp.route('/add_product', methods=['POST'])
def add_product():

    seller_id = session.get("user")
    if not seller_id:
        return redirect("api.logout")

    # product_id = request.form.get("product_id")
    category = request.form.get("category")
    product_name = request.form.get("product_name")
    quantity = request.form.get("quantity")
    price = request.form.get("price")
    status = 1
    product_description = request.form.get("product_description")
    product_title = request.form.get("product_title")
    try:
        product_id = get_prod_id(seller_id)
    except Exception as e:
        return f"error during product_id creation: {e}"

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("INSERT into Product_Listings (seller_email, listing_id, category, product_title, product_name, product_description, quantity, product_price, status) VALUES (?,?,?,?,?,?,?,?,?)",
                   [seller_id, product_id, category, product_title, product_name, product_description, quantity, price, status])
        db.commit()
    except sqlite3.IntegrityError as e:
        print(e)
        return f"Error: {e}"
    return redirect(url_for('api.get_seller_products'))


# gets products of a seller
@bp.route('/get_seller_products', methods=['GET','POST'])
def get_seller_products():
    seller_id = session.get("user")

    if not seller_id:
        return redirect(url_for('login.index'))

    status_filter = request.args.get('filter', 'active')

    db = get_db()
    db.row_factory = sqlite3.Row

    sql = "SELECT * FROM Product_Listings WHERE seller_email = ?"
    params = [seller_id]

    # last filter should be status = 2, but it works so don't touch it unless you have to
    if status_filter == 'active':
        sql += " AND status = 1"
    elif status_filter == 'inactive':
        sql += " AND status = 0"
    elif status_filter == 'soldout':
        sql += " AND quantity = 0"

    products = db.execute(sql, params).fetchall()
    print(products)

    return render_template("seller/index.html", products=products, status_filter=status_filter)

# this endpoint grabs top level categories
@bp.route('/top_level_categories', methods=['POST'])
def get_top_level_categories():
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
    return jsonify(result)


# this endpoint sets a request to inactive
@bp.route('/complete_request', methods=['POST'])
def complete_requests():
    req_id = request.form.get("request_id")

    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # status 0 is incomplete, 1 is complete - id must be passed as 1 element tuple
    try:
        cursor.execute("UPDATE requests SET request_status = 1 WHERE request_id = ?", (req_id,))
        db.commit()
    finally:
        db.close()

    return redirect(url_for('helpdesk.index'))
    # return f"Request #{req_id} marked complete"


# this grabs the requests for the helpdesk
@bp.route('/get_active_requests')
def get_active_requests():
    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # status 0 is incomplete, 1 is complete
    cursor.execute("SELECT * FROM requests WHERE request_status = 0")
    rows = cursor.fetchall()
    db.close()

    return render_template('helpdesk/index.html', result=rows)


# login checks if email and password match any row in the database
@bp.route("/users", methods=["POST"])
def login():
    emailS = request.form.get("email")
    password = hash_password(request.form.get("password"))

    if not validate_email(emailS) or not password:
        return redirect(url_for("login.index", login_failed=True))

    db = get_db()
    user = db.execute("SELECT * FROM Users WHERE email = ?", [emailS]).fetchone()

    if user is None or user["password"] != password:
        return redirect(url_for("login.index", login_failed=True))

    user_type = get_user_type(emailS)
    session["user"] = emailS
    session["user_type"] = user_type

    if user_type == "Buyer":
        return redirect(url_for("buyer.index"))
    elif user_type == "Seller":
        return redirect(url_for("seller.index"))
    else:
        return redirect(url_for("helpdesk.index"))

    return redirect(url_for("login.index", login_failed=True))


# Signup route for new user registration
@bp.route("/signup", methods=["POST"])
def signup():
    newEmail = request.form.get("email")
    newPassword = request.form.get("password")
    confirmPassowrd = request.form.get("passwordConf")
    accountType = request.form.get("accountType")

    if not validate_email(newEmail) or not newPassword or not confirmPassowrd:
        # if not newPassword or not confirmPassowrd:
        return redirect(url_for("signup.index", signup_failed=True))
    # match password
    if newPassword != confirmPassowrd:
        return redirect(url_for("signup.index", password_match_failed=True))

    if len(newPassword) < 8 or not any(char.isupper() for char in newPassword):
        return redirect(url_for("signup.index", password_requirements=True))

    db = get_db()

    try:
        # Check if the email already exists
        existing_user = db.execute("SELECT * FROM Users WHERE email = ?", [newEmail]).fetchone()
        if existing_user is not None:
            return redirect(url_for("signup.index", signup_exists=True))

        # Insert new user into the database
        hashed_password = hash_password(newPassword)
        db.execute("INSERT INTO Users (email, password) VALUES (?, ?)", [newEmail, hashed_password])
        db.commit()

        # Render different templates based on accountType
        if accountType == "seller":
            return render_template("signup/seller.html", email=newEmail)
        elif accountType == "buyer":
            return render_template("profile/buyerProfile.html", email=newEmail)
        else:
            return redirect(url_for("signup.index", signup_failed=True))


    except Exception as e:
        print(f"Database Error: {e}")
        return redirect(url_for("signup.index", signup_failed=True))


# updates all fields other than key/status
@bp.route("/product_update", methods=["POST"])
def product_update():
    print("💡 product_update received form:", request.form.to_dict())

    seller_email = session.get('user')
    listing_id = request.form.get("listing_id")
    # print(f"[DEBUG] product_update(): seller_email={seller_email!r}, listing_id={listing_id!r}")


    updated_count = update_listing(
                   seller_email,
                   listing_id,
                   category=request.form.get("category"),
                   product_title=request.form.get("product_title"),
                   product_name=request.form.get("product_name"),
                   product_description=request.form.get("product_description"),
                   status=request.form.get("status"),
                   quantity=request.form.get("quantity"),
                   product_price=int(float(request.form.get("product_price", 0)) * 100))


    # if updated_count:
    #     print(f"[DEBUG] update_listing → {updated_count} row(s) updated")
    # else:
    #     print("[DEBUG] update_listing → no rows updated (nothing changed or bad key)")

    return redirect(url_for('seller.index'))


#for placing orders
@bp.route("/place_order", methods=["POST"])
def place_order():
    buyer_id = session.get('user')
    # form for testing purposes, use session in prod
    # buyer_id = request.form.get("buyer_id")

    # listing id and seller email need to be grabbed from the page when an order is placed
    listing_id = request.form.get("listing_id")
    seller_email = request.form.get("seller_email")
    order_qty = int(request.form.get("quantity"))
    price = float(request.form.get("price"))
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    soldout = 2

    db = get_db()
    cursor = db.cursor()
    row = cursor.execute("SELECT * FROM Product_listings WHERE listing_id = ? AND seller_email = ?", [listing_id, seller_email]).fetchone()

    remainder = row["quantity"] - order_qty

    if row is None:
        return f"ERROR: ITEM DOES NOT EXIST"

    if row["status"] == 0:
        return f"Item is not available"
    if row["status"] == 2:
        return f"Item is sold out!"
    if remainder < 0:
        return f"Not enough items to sell"

    #creates order
    cursor.execute("INSERT INTO Orders (listing_id, seller_email, buyer_email, date, quantity, payment) VALUES (?,?,?,?,?,?)", (listing_id, seller_email, buyer_id, date, order_qty, price))

    #updates product listing/sets status if out of stock
    if remainder == 0:
        cursor.execute("UPDATE Product_Listings SET quantity = ?, status = ? WHERE listing_id = ? AND seller_email = ?", [remainder, soldout, listing_id, seller_email])
    else:
        cursor.execute("UPDATE Product_Listings SET quantity = ? WHERE listing_id = ? AND seller_email = ?", [remainder, listing_id, seller_email])

    db.commit()
    db.close()

    # return "Order placed successfully", 200
    return redirect(url_for("checkout.rate"))


#for a buyer to see their orders
@bp.route("/buyer_orders", methods=["POST"])
def buyer_orders():
    buyer_id = session.get('user')

    db = get_db()
    db.row_factory = sqlite3.Row
    rows = db.execute("SELECT * FROM Orders WHERE buyer_email = ?", [buyer_id]).fetchall()
    orders = [dict(row) for row in rows]
    db.close()

    return jsonify(orders)

# changes status of a product listing
# 1=active, 0=inactive, 2=soldout
@bp.route("/product_status_update", methods=["POST"])
def product_status_update():
    listing_id = request.form.get("listing_id")
    seller_email = session.get('user')
    status = request.form.get("status")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("UPDATE product_listings SET status = ? WHERE seller_email = ? AND listing_id = ?", (status, seller_email, listing_id))
    db.commit()

    return redirect(url_for('seller.index'))

# lets buyer leave rating on product
@bp.route("/new_prod_review", methods=["POST"])
def new_prod_review():
    order_id = request.form.get("order_id")
    review_desc = request.form.get("product_review")
    rating = request.form.get("product_rating")

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("INSERT into Reviews (order_id, review_desc, rate) VALUES (?,?,?)", (order_id, review_desc, rating))
        db.commit()
        db.close()
    except Exception as e:
        print(f"Database Error: {e}")
        return f"Error while inserting new review: {e}"
    return redirect(url_for("buyer.index"))

# lets buyer leave rating on product
@bp.route("/get_listing_reviews", methods=["POST"])
def get_listing_reviews():
    listing_id = request.form.get("listing_id")

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""SELECT * 
                        FROM Reviews AS r
                        JOIN Orders AS o
                        ON r.order_id = o.order_id
                        WHERE listing_id = ?""",
                       (listing_id,))
        rows = cursor.fetchall()
        db.close()
    except Exception as e:
        print(f"Database Error: {e}")
        return f"Error while getting listing reviews: {e}"
    result = [dict(row) for row in rows]
    return jsonify(result)

# gets average rating of all reviews for a given seller
@bp.route("/get_avg_seller_rating", methods=["POST"])
def get_avg_seller_rating():
    seller_id = request.form.get("seller_id")

    db = get_db()
    cursor = db.cursor()

    try:
        row = cursor.execute("""SELECT AVG(rate) AS avg_rating 
                                FROM Reviews AS r 
                                JOIN Orders AS o ON r.order_id = o.order_id 
                                JOIN Product_Listings AS p ON o.listing_id = p.listing_id 
                                WHERE p.seller_email = ?""",
                             (seller_id,)).fetchone()
        avg_rating = row[0]
    except Exception as e:
        print(f"Database Error: {e}")
        return f"Error while getting average seller rating: {e}"
    finally:
        db.close()
    return jsonify("average seller rating: ", str(avg_rating))

# Redirects to individual product page from productByCat
@bp.route("/to_product", methods=["POST"])
def to_product():
    listing_id = request.form.get("listing_id")
    business_name = request.form.get("business_name")

    db = get_db()
    cursor = db.cursor()

    try:
        row = cursor.execute("""SELECT *
                                FROM Product_Listings
                                WHERE listing_id = ?""",
                             (listing_id,)).fetchone()
    except Exception as e:
        print(f"Database Error: {e}")
        return f"Error while getting listing reviews: {e}"
    finally:
        db.close()

    return render_template("product/index.html", result=row, business_name=business_name)

# Redirects from individual product page to checkout
@bp.route("/product_to_checkout", methods=["POST"])
def product_to_checkout():
    listing_id = request.form.get("listing_id")
    order_quantity = request.form.get("order_quantity")
    product_price = request.form.get("product_price")
    business_name = request.form.get("business_name")

    db = get_db()
    cursor = db.cursor()

    try:
        row = cursor.execute("""SELECT *
                                    FROM Product_Listings
                                    WHERE listing_id = ?""",
                             (listing_id,)).fetchone()
    except Exception as e:
        print(f"Database Error: {e}")
        return f"Error while getting listing reviews: {e}"
    finally:
        db.close()

    total = int(order_quantity) * int(product_price)

    return render_template("checkout/index.html", result=row, quantity=order_quantity, total=total, business_name=business_name, listing_id=listing_id)


@bp.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return redirect(url_for("main.index"))

# testing auto-key on address table

@bp.route("/add_address", methods=["POST"])
def add_address():
    zipcode     = request.form.get("zipcode")
    street_num  = request.form.get("street_num")
    street_name = request.form.get("street_name")

    if not zipcode or not street_num or not street_name:
        return "Missing address fields", 400

    db     = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO Address (zipcode, street_num, street_name) VALUES (?, ?, ?)",
        (zipcode, street_num, street_name)
    )
    db.commit()
    address_id = cursor.lastrowid
    db.close()

    return jsonify({"address_id": address_id}), 201