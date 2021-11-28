import os
from sys import platform




from flask import app
from flask_mail import Mail

class Config:
       SECRET_KEY = os.environ.get('SECRET_KEY')
       SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
       UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
       MAIL_SERVER = 'smtp.googlemail.com'
       MAIL_PORT = 587
       MAIL_USE_TLS = True
       MAIL_USERNAME  = os.environ.get('MAIL_USERNAME')
       MAIL_PASSWORD =  os.environ.get('MAIL_PASSWORD')
       ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
       ALLOWED_FILE_EXTENSIONS = ["PNG", "JPG", "JPEG", "GIF", "PDF", "DOC", "TXT", "DOCX"]
