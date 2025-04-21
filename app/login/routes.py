from flask import render_template, request, session, redirect, url_for, flash
from app.login import bp


@bp.route('/')
def index():
    login_failed = request.args.get('login_failed', False)
    uid = request.args.get('uid', None)
    user = request.args.get('user_type', None)

    if not login_failed:
        session["user"] = uid
        session["user_type"] = user
        
        if user == "Buyer":
            return render_template('buyer/index.html')
        elif user == "Seller":
            return render_template('seller/index.html')
        else:
            return redirect(url_for('helpdesk.index'))
    return render_template('login/index.html', login_failed=login_failed)
