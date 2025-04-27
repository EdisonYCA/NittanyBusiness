from flask import Blueprint

bp = Blueprint('seller', __name__)

from app.seller import routes
