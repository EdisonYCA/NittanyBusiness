from flask import Flask
from config import Config
from flask import g
from config import Config

DB_PATH = Config.DB_PATH

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

    from app.product import bp as product_bp
    app.register_blueprint(product_bp, url_prefix='/product')

    from app.checkout import bp as checkout_bp
    app.register_blueprint(checkout_bp, url_prefix='/checkout')

    # app teardown tells db that connection is closing - refer to flask docs for details
    @app.teardown_appcontext
    def close_db(exception):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    return app

#trying to bypass import issues during refactoring
def get_db():
    from app.api.db_util import get_db as _get_db
    return _get_db()
