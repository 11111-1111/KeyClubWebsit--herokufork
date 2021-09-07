import os
from flask import app
from flask_mail import Mail


class GlobalVariables():    
    global admin_access
    admin_access = None

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
    ALLOWED_FILE_EXTENSIONS = ["PNG", "JPG", "JPEG", "GIF", "PDF", "DOC", "TXT", "DOCX"]
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME  = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD =  os.environ.get('EMAIL_PASS')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
