from flask import render_template, request, session, redirect, url_for, flash
from app.login import bp


@bp.route('/')
def index():
    failed = request.args.get("login_failed", False)
    return render_template('login/index.html', login_failed=failed)