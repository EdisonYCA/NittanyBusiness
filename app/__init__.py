from flask import Flask
from config import Config
import sqlite3
from flask import g

DB_PATH = 'database.db'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.login import bp as login_bp
    app.register_blueprint(login_bp, url_prefix='/login')

    from app.signup import bp as signup_bp
    app.register_blueprint(signup_bp, url_prefix='/signup')

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.helpdesk import bp as helpdesk_bp
    app.register_blueprint(helpdesk_bp, url_prefix='/helpdesk')

    # app teardown tells db that connection is closing - refer to flask docs for details
    @app.teardown_appcontext
    def close_db(exception):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    return app


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db
