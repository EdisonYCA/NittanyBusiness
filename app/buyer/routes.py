from flask import render_template, request
from app.buyer import bp


@bp.route('/')
def index():
    return render_template('buyer/index.html')
