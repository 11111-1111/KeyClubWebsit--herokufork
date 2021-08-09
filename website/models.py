from . import db
from flask_login import UserMixin




class login_details(db.Model, UserMixin):
    id = db.Column(db.String(100),primary_key = True)
    password = db.Column(db.String(20))


class student_info(db.Model, UserMixin):
    student_id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(100), unique = True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    current_hours = db.Column(db.Float)
    pending_hours = db.Column(db.Float)
    boardMember = db.Column(db.Boolean)
    inductedMember = db.Column(db.Boolean)
    verifiedMember = db.Column(db.Boolean)

class event_info(db.Model):
    event_id = db.Column(db.Integer, primary_key = True)
    event_name = db.Column(db.String(100))
    event_time = db.Column(db.DateTime(timezone = True))
    more_info = db.Column(db.String(100))
    event_type = db.Column(db.String(50))
    event_reccurent = db.Column(db.Boolean)
    spots_available = db.Column(db.Integer)

class registration(db.Model):
    event_id = db.Column(db.Integer, db.ForeignKey('event_info.event_id'), primary_key = True)
    student_id = db.Column(db.Integer,db.ForeignKey('student_info.student_id'), primary_key = True)
    status = db.Column(db.String(15))
    comments = db.Column(db.String(100))
    time_submitted = db.Column(db.DateTime(timezone = True))

class recurring_events(db.Model):
    event_id = db.Column(db.Integer, db.ForeignKey('event_info.event_id'),  primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_info.student_id'), primary_key = True)
    numb_of_hours = db.Column(db.Float())
















