from app.buyer import bp
from flask import render_template
from app.utils.auth import login_required


@bp.route('/')
@login_required
def index():
    return render_template('buyer/index.html')

@bp.route('/search', methods=['POST'])
def search():
    return render_template('buyer/search.html')