from urllib.parse import quote_plus
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
db = SQLAlchemy()
mail = Mail()
import os

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "Some_key"

    password = quote_plus('1994')
    chaine = "postgresql://postgres:{}@localhost:5432/gestion".format(password)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

    # postgres://gestion_8a61_user:vJMdhHZUH0MTYjQMa2uL4kQUz7Lj8j5I@dpg-ck1etf1gbqfc73845o90-a.oregon-postgres.render.com/gestion_8a61

    # app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    # app.config['MAIL_PORT']   = 465
    # app.config['MAIL_USERNAME']   = 'admin admin'
    # app.config['MAIL_DEFAULT_SENDER']   = 'maestro.master.003@gmail.com'
    # app.config['MAIL_PASSWORD']   = 'KOMla*200'
    # app.config['MAIL_USE_TLS']   = False
    # app.config['MAIL_USE_SSL']   = True

    db.init_app(app)
    mail.init_app(app)

    migrate = Migrate(app, db)



    from .auth import auth
    from .views_admin import views_admin
    from .views_client import views_client

    from .models import Users

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(int(id))

    with app.app_context(): 
        db.create_all()

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(views_admin, url_prefix="/admin")
    app.register_blueprint(views_client, url_prefix="/client")
    
    @app.route('/')
    def default_route():
        return redirect(url_for('auth.login'))


    return app