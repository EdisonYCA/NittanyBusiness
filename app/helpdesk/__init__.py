from flask import Blueprint

bp = Blueprint('helpdesk', __name__)

from app.helpdesk import routes