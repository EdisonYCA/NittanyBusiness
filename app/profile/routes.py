from flask import request, redirect, url_for, render_template, session
from app import get_db
from app.api import bp
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
    password_match_failed = request.args.get('password_match_failed', False)
    oldMatchingPassword = request.args.get('oldMatchingPassword', False)
    password_requirements = request.args.get('password_requirements', False)
    profile_failed = request.args.get('profile_failed', False)
    return render_template('profile/buyerProfile.html', oldMatchingPassword=oldMatchingPassword,
                           password_match_failed=password_match_failed, password_requirements=password_requirements, profile_failed = profile_failed)

@bp.route('/sellerProfile', methods=['POST'])
def sellerProfileLoad():
    password_match_failed = request.args.get('password_match_failed', False)
    oldMatchingPassword = request.args.get('oldMatchingPassword', False)
    password_requirements = request.args.get('password_requirements', False)
    profile_failed = request.args.get('profile_failed', False)
    return render_template('profile/sellerProfile.html', oldMatchingPassword=oldMatchingPassword,
                           password_match_failed=password_match_failed, password_requirements=password_requirements, profile_failed = profile_failed)



def hash_password(password):
    if not password:
        return ""

    sha256 = hashlib.new("SHA256")
    sha256.update(password.encode())
    hashed_password = sha256.hexdigest()
    return hashed_password

@bp.route('/update', methods=['POST'])
def update():
    oldPassword = request.args.get('oldPasswordInput')
    newPassword = request.args.get('newPasswordInput')
    confNewPassword = request.args.get('confirmPasswordInput')
    ccNumber = request.args.get('creditCardNumberInput')
    ccExpiration = request.args.get('expirationDateInput')
    ccType = request.args.get('cardTypeInput')
    streetAddress = request.args.get('addressInput')
    city = request.args.get('cityInput')
    state = request.args.get('stateInput')
    zipCode = request.args.get('zipInput')
    #check
    user_email = session.get("email")
    #user_email = "sjy5323@psu.edu"
    if not user_email:
        return redirect(url_for("login.index", login_failed=True))
    db = get_db()
    try:
        if oldPassword == newPassword:
            #return new password must be different
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

        # Update credit card information in the database
        db.execute("""
                    INSERT INTO CreditCards (user_email, card_number, expiration_date, card_type) 
                    VALUES (?, ?, ?, ?) ON CONFLICT(user_email) DO UPDATE SET
                    ccNumber = excluded.card_number,
                    ccExpiration = excluded.expiration_date,
                    ccType = excluded.card_type
                """, [user_email, ccNumber, ccExpiration, ccType])

        # Update address information in the database
        db.execute("""
                    INSERT INTO Address (user_email, address, city, state, zip) 
                    VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_email) DO UPDATE SET
                    streetAddress = excluded.address,
                    city = excluded.city,
                    state = excluded.state,
                    zipCode = excluded.zip
                """, [user_email, streetAddress, city, state, zipCode])

        db.commit()
        return render_template("profile/success.html", email=user_email)

    except Exception as e:
        print(f"Database Error: {e}")
        return redirect(url_for("profile.index", profile_failed=True))



@bp.route('/logOut', methods=['POST'])
def switch_profile():
    # Clear session to log out the current user
    session.clear()
    return redirect(url_for("login.index", logOut=True))

@bp.route('/delete_user', methods=['POST'])
def delete_profile():
    user_email = session.get("email")
    if not user_email:
        return redirect(url_for("login.index", login_failed=True))

    db = get_db()

    try:
        # Delete user data from related tables
        db.execute("DELETE FROM CreditCards WHERE user_email = ?", [user_email])
        db.execute("DELETE FROM Address WHERE user_email = ?", [user_email])

        # Delete user record
        db.execute("DELETE FROM Users WHERE email = ?", [user_email])
        db.commit()

        session.clear()  # Clear session after deletion
        return redirect(url_for("signup.index", user_deleted=True))

    except Exception as e:
        print(f"Delete Profile Error: {e}")
        return redirect(url_for("profile.index", profile_failed=True))

@bp.route('/switch_account_type', methods=['POST'])
def switch_account_type():
        user_email = session.get("email")
        if not user_email:
            return redirect(url_for("login.index", login_failed=True))

        db = get_db()

        try:
            # Get the current account type
            user = db.execute("SELECT account_type FROM Users WHERE email = ?", [user_email]).fetchone()
            if user is None:
                return redirect(url_for("login.index", login_failed=True))

            current_account_type = user["account_type"]

            if current_account_type == "buyer":
                # Delete all products the user is buying check this with ritchie
                db.execute("DELETE FROM Orders WHERE buyer_email = ?", [user_email])

                # Switch account type to seller
                db.execute("UPDATE Users SET account_type = ? WHERE email = ?", ["seller", user_email])
                db.commit()
                return redirect(url_for("profile.index", switched_to="seller"))

            elif current_account_type == "seller":
                # Delete all products the user is selling check this with ritchie
                db.execute("DELETE FROM Products WHERE seller_email = ?", [user_email])

                # Switch account type to buyer
                db.execute("UPDATE Users SET account_type = ? WHERE email = ?", ["buyer", user_email])
                db.commit()
                return redirect(url_for("profile.index", switched_to="buyer"))

            else:
                # Handle unknown account types
                print(f"Unknown account type for user: {user_email}")
                return redirect(url_for("profile.index", profile_failed=True))

        except Exception as e:
            print(f"Switch Account Type Error: {e}")
            return redirect(url_for("profile.index", profile_failed=True))

    #to change userID contact helpdesk, to switch useer contact helpdesk, to add new category contact helpdesk
