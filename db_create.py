from __init__ import db
from views import app
db.init_app(app)

with app.app_context():
  db.create_all() 
