

from flask import request, redirect, url_for, render_template, session, jsonify
from app import get_db
from app.profile import bp
import hashlib
import re
from app.profile import bp

@bp.route('/')
def index():
    password_match_failed = request.args.get('password_match_failed', False)
    oldMatchingPassword = request.args.get('oldMatchingPassword', False)
    password_requirements = request.args.get('password_requirements', False)
    profile_failed = request.args.get('profile_failed', False)
    return render_template('profile.html', oldMatchingPassword=oldMatchingPassword, password_match_failed= password_match_failed, password_requirements = password_requirements)

@bp.route('/buyerProfile', methods=['POST'])
def buyerProfileLoad():
    user_email = session.get("email")
    db = get_db()
    user = db.execute("SELECT * FROM Users WHERE email = ?", [user_email]).fetchone()
    address = db.execute("""
            SELECT A.*, Z.city, Z.state
            FROM Address A
            JOIN Buyers B ON B.buyer_address_id = A.address_id
            JOIN Zipcode_Info Z ON A.zipcode = Z.zipcode
            WHERE B.email = ?
        """, [user_email]).fetchone()
    credit_card = db.execute("SELECT * FROM Credit_Cards WHERE owner_email = ?", [user_email]).fetchone()
    password_match_failed = request.args.get('password_match_failed', False)
    oldMatchingPassword = request.args.get('oldMatchingPassword', False)
    password_requirements = request.args.get('password_requirements', False)
    profile_failed = request.args.get('profile_failed', False)
    delete_failed = request.args.get('delete_failed', False)
    return render_template('profile/buyerProfile.html',
                           user = user,
                           address = address,
                           credit_card = credit_card,
                           oldMatchingPassword=oldMatchingPassword,
                           password_match_failed=password_match_failed,
                           password_requirements=password_requirements,
                           profile_failed = profile_failed, delete_failed=delete_failed)

@bp.route('/sellerProfile', methods=['POST'])
def sellerProfileLoad():
    user_email = session.get('user_email')
    db = get_db()
    user = db.execute("SELECT * FROM Users WHERE email = ?", [user_email]).fetchone()
    address = db.execute("""
        SELECT A.*, Z.city, Z.state
        FROM Address A
        JOIN Sellers S ON S.business_address_id = A.address_id
        JOIN Zipcode_Info Z ON A.zipcode = Z.zipcode
        WHERE S.email = ?
    """, [user_email]).fetchone()
    seller_bank_info = db.execute("SELECT bank_routing_number, bank_account_number FROM Sellers WHERE email = ?", [user_email]).fetchone()
    password_match_failed = request.args.get('password_match_failed', False)
    oldMatchingPassword = request.args.get('oldMatchingPassword', False)
    password_requirements = request.args.get('password_requirements', False)
    profile_failed = request.args.get('profile_failed', False)
    return render_template('profile/sellerProfile.html',
                           user = user,
                           address = address,
                           bank_info = seller_bank_info,
                           oldMatchingPassword=oldMatchingPassword,
                           password_match_failed=password_match_failed,
                           password_requirements=password_requirements,
                           profile_failed = profile_failed)



def hash_password(password):
    if not password:
        return ""

    sha256 = hashlib.new("SHA256")
    sha256.update(password.encode())
    hashed_password = sha256.hexdigest()
    return hashed_password


@bp.route('/update', methods=['POST'])
def update():
    oldPassword = request.form.get('oldPasswordInput')
    newPassword = request.form.get('newPasswordInput')
    confNewPassword = request.form.get('confirmPasswordInput')
    ccNumber = request.form.get('creditCardNumberInput')
    ccExpireMonth = request.form.get('expirationMonthInput')
    ccExpireYear = request.form.get('expirationYearInput')
    ccSecurityCode = request.form.get('securityCodeInput')
    ccType = request.form.get('cardTypeInput')
    streetNum = request.form.get('streetNumInput')
    streetName = request.form.get('streetNameInput')
    zipCode = request.form.get('zipInput')
    city = request.form.get('cityInput')
    state = request.form.get('stateInput')

    user_email = session.get("email")
    if not user_email:
        return redirect(url_for("login.index", login_failed=True))

    db = get_db()
    try:
        # Password validation
        if oldPassword == newPassword:
            return redirect(url_for("profile.index", oldMatchingPassword=True))
        if newPassword != confNewPassword:
            return redirect(url_for("profile.index", password_match_failed=True))
        if len(newPassword) < 8 or not any(char.isupper() for char in newPassword):
            return redirect(url_for("profile.index", password_requirements=True))

        user = db.execute("SELECT * FROM Users WHERE email = ?", [user_email]).fetchone()
        if user is None or hash_password(oldPassword) != user["password"]:
            return redirect(url_for("profile.index", profile_failed=True))

        hashed_password = hash_password(newPassword)
        db.execute("UPDATE Users SET password = ? WHERE email = ?", [hashed_password, user_email])

        # Update Credit_Cards table
        db.execute("""
            INSERT OR REPLACE INTO Credit_Cards (credit_card_num, card_type, expire_month, expire_year, security_code, owner_email)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [ccNumber, ccType, ccExpireMonth, ccExpireYear, ccSecurityCode, user_email])

        # Update Address table
        db.execute("""
            INSERT OR REPLACE INTO Address (address_id, street_num, street_name, zipcode)
            VALUES (?, ?, ?, ?)
        """, [f"{streetNum} {streetName}", streetNum, streetName, zipCode])

        # Update Zipcode_Info table
        db.execute("""
            INSERT OR REPLACE INTO Zipcode_Info (zipcode, city, state)
            VALUES (?, ?, ?)
        """, [zipCode, city, state])

        db.commit()
        return render_template("profile/success.html", email=user_email)
    except Exception as e:
        print(f"Database Error: {e}")
        return redirect(url_for("profile.index", profile_failed=True))



@bp.route('/updateBuyerProfile', methods=['POST'])
def update_buyer_profile():
    user_email = session.get("email")
    if not user_email:
        return redirect(url_for("login.index", login_failed=True))

    # Get form data
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    street_num = request.form.get('street_num')
    street_name = request.form.get('street_name')
    zipcode = request.form.get('zipcode')
    city = request.form.get('city')
    state = request.form.get('state')

    credit_card_num = request.form.get('credit_card_num')
    card_type = request.form.get('card_type')
    expire_month = request.form.get('expire_month')
    expire_year = request.form.get('expire_year')
    security_code = request.form.get('security_code')

    db = get_db()
    try:
        # Validate and update password
        if old_password and new_password and confirm_password:
            user = db.execute("SELECT * FROM Users WHERE email = ?", [user_email]).fetchone()
            if not user or hash_password(old_password) != user["password"]:
                return redirect(url_for("profile.buyerProfileLoad", profile_failed=True))

            if new_password != confirm_password:
                return redirect(url_for("profile.buyerProfileLoad", password_match_failed=True))

            if len(new_password) < 8 or not any(char.isupper() for char in new_password):
                return redirect(url_for("profile.buyerProfileLoad", password_requirements=True))

            hashed_password = hash_password(new_password)
            db.execute("UPDATE Users SET password = ? WHERE email = ?", [hashed_password, user_email])

        # Update address information
        if street_num and street_name and zipcode and city and state:
            address_id = f"{street_num}_{street_name}_{zipcode}"
            db.execute("""
                INSERT OR REPLACE INTO Address (address_id, street_num, street_name, zipcode)
                VALUES (?, ?, ?, ?)
            """, [address_id, street_num, street_name, zipcode])

            db.execute("""
                INSERT OR REPLACE INTO Zipcode_Info (zipcode, city, state)
                VALUES (?, ?, ?)
            """, [zipcode, city, state])

            db.execute("""
                UPDATE Buyers SET buyer_address_id = ? WHERE email = ?
            """, [address_id, user_email])

        # Update credit card information
        if credit_card_num and card_type and expire_month and expire_year and security_code:
            db.execute("""
                INSERT OR REPLACE INTO Credit_Cards (credit_card_num, card_type, expire_month, expire_year, security_code, owner_email)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [credit_card_num, card_type, expire_month, expire_year, security_code, user_email])

        db.commit()
        return redirect(url_for("profile.buyerProfileLoad", success=True))
    except Exception as e:
        print(f"Buyer Profile Update Error: {e}")
        return redirect(url_for("profile.buyerProfileLoad", profile_failed=True))





@bp.route('/updateSellerProfile', methods=['POST'])
def update_seller_profile():
    user_email = session.get("email")
    if not user_email:
        return redirect(url_for("login.index", login_failed=True))

    # Get form data
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    street_num = request.form.get('street_num')
    street_name = request.form.get('street_name')
    zipcode = request.form.get('zipcode')
    city = request.form.get('city')
    state = request.form.get('state')

    bank_routing_number = request.form.get('bank_routing_number')
    bank_account_number = request.form.get('bank_account_number')

    db = get_db()
    try:
        # Validate and update password
        if old_password and new_password and confirm_password:
            user = db.execute("SELECT * FROM Users WHERE email = ?", [user_email]).fetchone()
            if not user or hash_password(old_password) != user["password"]:
                return redirect(url_for("profile.sellerProfileLoad", profile_failed=True))

            if new_password != confirm_password:
                return redirect(url_for("profile.sellerProfileLoad", password_match_failed=True))

            if len(new_password) < 8 or not any(char.isupper() for char in new_password):
                return redirect(url_for("profile.sellerProfileLoad", password_requirements=True))

            hashed_password = hash_password(new_password)
            db.execute("UPDATE Users SET password = ? WHERE email = ?", [hashed_password, user_email])

        # Update business address information
        if street_num and street_name and zipcode and city and state:
            address_id = f"{street_num}_{street_name}_{zipcode}"
            db.execute("""
                INSERT OR REPLACE INTO Address (address_id, street_num, street_name, zipcode)
                VALUES (?, ?, ?, ?)
            """, [address_id, street_num, street_name, zipcode])

            db.execute("""
                INSERT OR REPLACE INTO Zipcode_Info (zipcode, city, state)
                VALUES (?, ?, ?)
            """, [zipcode, city, state])

            db.execute("""
                UPDATE Sellers SET business_address_id = ? WHERE email = ?
            """, [address_id, user_email])

        # Update bank details
        if bank_routing_number and bank_account_number:
            db.execute("""
                UPDATE Sellers SET
                    bank_routing_number = ?,
                    bank_account_number = ?
                WHERE email = ?
            """, [bank_routing_number, bank_account_number, user_email])

        db.commit()
        return redirect(url_for("profile.sellerProfileLoad", success=True))
    except Exception as e:
        print(f"Seller Profile Update Error: {e}")
        return redirect(url_for("profile.sellerProfileLoad", profile_failed=True))





@bp.route('/delete_user', methods=['POST'])
def delete_profile():
    user_email = session.get("email")
    if not user_email:
        return redirect(url_for("login.index", login_failed=True))

    db = get_db()
    try:
        # Delete user data from all related tables
        db.execute("DELETE FROM Credit_Cards WHERE owner_email = ?", [user_email])
        db.execute("DELETE FROM Buyers WHERE email = ?", [user_email])
        db.execute("DELETE FROM Sellers WHERE email = ?", [user_email])
        db.execute("DELETE FROM Users WHERE email = ?", [user_email])

        db.commit()
        session.clear()
        return redirect(url_for("signup.index", delete_failed=False))
    except Exception as e:
        print(f"Delete Profile Error: {e}")
        return redirect(url_for("profile.index", delete_failed=True))


@bp.route('/switch_account_type', methods=['POST'])
def switch_account_type():
    user_email = session.get("email")
    if not user_email:
        return redirect(url_for("login.index", login_failed=True))

    db = get_db()

    try:
        # Fetch the current account type for the user
        user = db.execute("SELECT * FROM Buyers WHERE email = ?", [user_email]).fetchone()
        if user:
            current_account_type = "buyer"
        else:
            user = db.execute("SELECT * FROM Sellers WHERE email = ?", [user_email]).fetchone()
            current_account_type = "seller" if user else None

        # If user is neither a buyer nor a seller, return an error
        if not current_account_type:
            return redirect(url_for("login.index", profile_failed=True))

        # Switch from buyer to seller
        if current_account_type == "buyer":
            # Delete the user from the Buyers table
            db.execute("DELETE FROM Buyers WHERE email = ?", [user_email])

            # Insert the user into the Sellers table
            db.execute("""
                INSERT INTO Sellers (email, business_name, business_address_id, bank_routing_number, bank_account_number, balance)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [user_email, "New Seller Business", "default_address_id", 0, 0, 0.0])

            db.commit()
            return redirect(url_for("profile.sellerProfileLoad", switched_to="seller"))

        # Switch from seller to buyer
        elif current_account_type == "seller":
            # Delete the user from the Sellers table
            db.execute("DELETE FROM Sellers WHERE email = ?", [user_email])

            # Insert the user into the Buyers table
            db.execute("""
                INSERT INTO Buyers (email, business_name, buyer_address_id)
                VALUES (?, ?, ?)
            """, [user_email, "New Buyer Business", "default_address_id"])

            db.commit()
            return redirect(url_for("profile.buyerProfileLoad", switched_to="buyer"))

        else:
            # Handle unknown account types
            print(f"Unknown account type for user: {user_email}")
            return redirect(url_for("profile.index", profile_failed=True))

    except Exception as e:
        print(f"Switch Account Type Error: {e}")
        return redirect(url_for("profile.index", profile_failed=True))

    #to change userID contact helpdesk, to switch useer contact helpdesk, to add new category contact helpdesk
@bp.route('/logOut', methods=['POST'])
def logOut():
