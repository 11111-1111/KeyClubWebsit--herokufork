import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()
from os import path
from flask_login import LoginManager
from Config import Config



def create_app(): 
    print("hello")
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    from views import views
    from auth import auth 
    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')
    from models import student_info, login_details, event_info, registration, recurring_events
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return student_info.query.get(id)

    create_database(app)

    
  
    return app


def create_database(app):
    if not path.exists('website/' + "database.db"):
        db.create_all(app = app)
        print("Created Database")
    


    



