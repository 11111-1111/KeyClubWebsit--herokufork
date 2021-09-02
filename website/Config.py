import os
import json

with open('/etc/config.json') as config_file:
    config = json.load(config_file)
    print("made it")

class Config:
    SECRET_KEY = config.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    UPLOAD_FOLDER = config.get('UPLOAD_FOLDER')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME  = config.get('EMAIL_USER')
    MAIL_PASSWORD =  config.get('EMAIL_PASS')
    ALLOWED_FILE_EXTENSIONS = ["PNG", "JPG", "JPEG", "GIF", "PDF", "DOC", "TXT", "DOCX"]
