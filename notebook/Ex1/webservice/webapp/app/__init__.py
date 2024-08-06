from flask import Flask
from app.config import Config
from app.models import db, bcrypt, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'

    with app.app_context():
        db.create_all()

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
