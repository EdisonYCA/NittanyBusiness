from flask import render_template, request
from app.login import bp


@bp.route('/')
def index():
    login_failed = request.args.get('login_failed', False)
    return render_template('login/index.html', login_failed=login_failed)
