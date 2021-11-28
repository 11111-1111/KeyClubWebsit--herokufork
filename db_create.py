#to destroy the database:
# 1. cd to github folder, and run: heroku git:remote -a key-club
# 2. run heroku pg:reset DATABASE


#the code below creates the postgres database. To run it, go to heroku console and run: python db_create.py

from __init__ import db
from views import app
db.init_app(app)

with app.app_context():
  db.create_all() 
