from __init__ import db
from views import app

with app.app_context():
  db.create_all() 
