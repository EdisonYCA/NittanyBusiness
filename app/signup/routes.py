from flask import render_template, request, redirect, url_for, jsonify, session
from app.signup import bp
from app.utils import auth
from app import get_db
import uuid

@bp.route('/')
def index():
    signup_failed = request.args.get('signup_failed', False)
    signup_exists = request.args.get('signup_exists', False)
    password_match_failed = request.args.get('password_match_failed', False)
    password_requirements = request.args.get('password_requirements', False)
    return render_template('signup/index.html', signup_failed=signup_failed,
                           signup_exists=signup_exists,
                           password_match_failed=password_match_failed,
                           password_requirements = password_requirements)

@bp.route("/signup", methods=["POST"])
def signup():
    newEmail = request.form.get("email")
    newPassword = request.form.get("password")
    confirmPassword = request.form.get("passwordConf")
    accountType = request.form.get("accountType")

    # Validate Password and Email Requirements
    if not auth.validate_email(newEmail) or not newPassword or not confirmPassword:
        return redirect(url_for("signup.index", signup_failed=True))

    if newPassword != confirmPassword:
        return redirect(url_for("signup.index", password_match_failed=True))

    if len(newPassword) < 8 or not any(char.isupper() for char in newPassword):
        return redirect(url_for("signup.index", password_requirements=True))

    db = get_db()
    try:
        # Confirm New User
        existing_user = db.execute("SELECT * FROM Users WHERE email = ?", [newEmail]).fetchone()
        if existing_user is not None:
            return redirect(url_for("signup.index", signup_exists=True))

        # Insert the new user into the Users table
        hashed_password = auth.hash_password(newPassword)
        db.execute("INSERT INTO Users (email, password) VALUES (?, ?)", [newEmail, hashed_password])
        db.commit()

        # Re-direct to Next Sign-Up Page
        if accountType == "seller":
            return render_template("signup/seller.html", email=newEmail)
        elif accountType == "buyer":
            return render_template("signup/buyer.html", email=newEmail)
        elif accountType.lower() == "helpdesk":
            return render_template("signup/helpdesk.html", email=newEmail)
        else:
            return redirect(url_for("signup.index", signup_failed=True))
    except Exception as e:
        return jsonify(f"Database Error: {e}")


@bp.route('/signupSeller', methods=['POST'])
def signupSeller():
    email = request.form.get('uid')
    street_num = request.form.get('street_num')
    street_name = request.form.get('street_name')
    zipcode = request.form.get('zipcode')
    bank_routing_number = request.form.get('bank_routing_number')
    bank_account_number = request.form.get('bank_account_number')
    businessName = request.form.get("businessName")

    db = get_db()
    try:
        # Insert Address
        address_id = uuid.uuid4().hex
        db.execute("INSERT INTO Address (address_id, street_num, street_name, zipcode) VALUES (?, ?, ?, ?)",
                   [address_id, street_num, street_name, zipcode])

        # Insert Seller Information
        db.execute("""
                INSERT INTO Sellers (email, business_name, business_address_id, bank_routing_number, bank_account_number, balance)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [email, businessName, address_id, bank_routing_number, bank_account_number, 0.0])

        db.commit()
        session["user"] = email
        session["user_type"] = "Seller"

        return render_template("seller/index.html", email=email)
    except Exception as e:
        print(e)
        return render_template("seller/index.html", error=True)


@bp.route('/signupBuyer', methods=['POST'])
def signupBuyer():
    email = request.form.get('email')
    street_num = request.form.get('street_num')
    street_name = request.form.get('street_name')
    zipcode = request.form.get('zipcode')
    credit_card_num = request.form.get('credit_card_num')
    card_type = request.form.get('card_type')
    expire_month = request.form.get('expire_month')
    expire_year = request.form.get('expire_year')
    security_code = request.form.get('security_code')
    business_name = request.form.get("business_name")

    db = get_db()
    try:
        # Insert Address and Zipcode_Info
        address_id = uuid.uuid4().hex
        db.execute("INSERT INTO Address (address_id, street_num, street_name, zipcode) VALUES (?, ?, ?, ?)",
                   [address_id, street_num, street_name, zipcode])

        # Insert Buyer and Credit Card
        db.execute("INSERT INTO Buyers (email, business_name, buyer_address_id) VALUES (?, ?, ?)",
                   [email, business_name, address_id])
        db.execute("""
                             INSERT INTO Credit_Cards (credit_card_num, card_type, expire_month, expire_year, security_code, owner_email)
                             VALUES (?, ?, ?, ?, ?, ?)
                         """, [credit_card_num, card_type, expire_month, expire_year, security_code, email])

        db.commit()
        session["user"] = email
        session["user_type"] = "Buyer"

        return render_template("buyer/index.html", email=email)
    except Exception as e:
        print(e)
        return render_template("buyer/index.html", error=True)