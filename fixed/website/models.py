from . import db
from flask_login import UserMixin
from datetime import datetime




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
    student_registered = db.relationship('registration', backref = 'student')

class event_info(db.Model, UserMixin):
    event_id = db.Column(db.Integer, primary_key = True)
    event_name = db.Column(db.String(100))
    event_time = db.Column(db.DateTime(timezone = True))
    event_location = db.Column(db.String(200))
    event_hours = db.Column(db.Float)
    more_info = db.Column(db.String(1000))
    event_type = db.Column(db.String(50))
    event_reccurent = db.Column(db.Boolean)    
    spots_available = db.Column(db.Integer)
    event_registered = db.relationship('registration', backref = 'event')


class registration(db.Model):
    idreg = db.Column(db.Integer, autoincrement = True,  primary_key = True)
    status = db.Column(db.String(15))
    comments = db.Column(db.String(100))
    time_submitted = db.Column(db.DateTime(timezone = True))
    event_id = db.Column(db.Integer, db.ForeignKey('event_info.event_id'))
    student_id = db.Column(db.Integer,db.ForeignKey('student_info.student_id'))

class recurring_events(db.Model):
    event_id = db.Column(db.Integer, db.ForeignKey('event_info.event_id'),  primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_info.student_id'), primary_key = True)
    numb_of_hours = db.Column(db.Float())


class announcements(db.Model):
    announcement_id = db.Column(db.Integer, primary_key = True)
    announcement_date_time = db.Column(db.DateTime(timezone= True), default=datetime.utcnow)
    announcement_title = db.Column(db.String(1000))
    announcement = db.Column(db.String(100000))
    announcement_file = db.Column(db.LargeBinary, default = None)



















