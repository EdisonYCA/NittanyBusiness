from flask import render_template, request
from app.signup import bp


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


def signupHelpDesk():
    auth_failed = request.args.get('auth_failed', False)
    return render_template('signup/index.html', auth_failed=auth_failed)