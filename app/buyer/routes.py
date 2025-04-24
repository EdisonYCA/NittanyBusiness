from app.buyer import bp
from flask import render_template, request
from app.utils.auth import login_required
import sqlite3
from app import get_db


@bp.route('/')
@login_required
def index():
    return render_template('buyer/index.html')

@bp.route('/search', methods=['POST'])
def search():
    search_val = request.form.get('search')

    return render_template('buyer/search.html', search=search_val)