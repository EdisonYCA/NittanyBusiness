from flask import Blueprint

bp = Blueprint('signup', __name__)


from app.signup import routes