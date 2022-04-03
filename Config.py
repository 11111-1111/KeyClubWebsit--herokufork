import os
from sys import platform




from flask import app
from flask_mail import Mail

class Config:
       SECRET_KEY = os.environ.get('SECRET_KEY')
       SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
       if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
              SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
       UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
       MAIL_SERVER = 'smtp.googlemail.com'
       MAIL_PORT = 587
       MAIL_USE_TLS = True
       MAIL_USERNAME  = os.environ.get('MAIL_USERNAME')
       MAIL_PASSWORD =  os.environ.get('MAIL_PASSWORD')
       ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
       ALLOWED_FILE_EXTENSIONS = ["PNG", "JPG", "JPEG", "GIF", "PDF", "DOC", "TXT", "DOCX"]
       SECRET_KEY_FORM = "Secret Key"
       RECAPTCHA_PUBLIC_KEY = "6Le-vT0fAAAAAIIMCwKaGsl8OFOjA2C9mI0Obun4"
       RECAPTCHA_PRIVATE_KEY = "6Le-vT0fAAAAANSwwTctmUuy1lam8Y_ad5q41lkD"
       CLOUD_NAME = os.environ.get('CLOUD_NAME')
       API_KEY = os.environ.get('API_KEY')
       API_SECRET = os.environ.get('API_SECRET')
