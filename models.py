from flask_login import UserMixin
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.sql.functions import current_user
from __init__ import db 
from views import app
from Config import Config
from flask_mail import Message, Mail
#from _typeshed import Self


class login_details(db.Model, UserMixin):
    id = db.Column(db.String(100),primary_key = True)
    password = db.Column(db.String(257))



class student_info(db.Model, UserMixin):
    student_id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(100), unique = True)
    first_name = db.Column(db.String(20))  
    last_name = db.Column(db.String(20))
    current_hours = db.Column(db.Float)
    pending_hours = db.Column(db.Float)
    boardMember = db.Column(db.Boolean)
    inductedMember = db.Column(db.Boolean)
    announcementnotifications = db.Column(db.Boolean)
    approvalnotifications =  db.Column(db.Boolean)
    eventnotifcations = db.Column(db.Boolean)
    student_registered = db.relationship('registration', backref = 'student')

    def sendemail(self, message, body):
        app.config.from_object(Config)
        msg = Message(message, sender='raymondmoy11@gmail.com', recipients=[self.email])
        msg.body = body
        mail = Mail(app) 
        mail.init_app(app)
        mail.send(msg)
 





    def get_reset_token(self, expires_sec=1800):
        app.config.from_object(Config)
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.student_id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        app.config.from_object(Config)
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return student_info.query.get(user_id)

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
    event_filename = db.Column(db.String(1000), default= None)





class registration(db.Model, UserMixin):
    idreg = db.Column(db.Integer, autoincrement = True,  primary_key = True)
    status = db.Column(db.String(15))
    comments = db.Column(db.String(100))
    time_submitted = db.Column(db.DateTime(timezone = True))
    event_id = db.Column(db.Integer, db.ForeignKey('event_info.event_id'))
    student_id = db.Column(db.Integer,db.ForeignKey('student_info.student_id'))
    decision_time = db.Column(db.DateTime(timezone = True))
    decision_student = db.Column(db.String(1000))
    hours_given = db.Column(db.Integer)


    def undo(self):
        if(self.status == 'Accepted'):
            self.student.current_hours = self.student.current_hours - self.hours_given
        self.status = 'Waiting'
        self.student.pending_hours = self.student.pending_hours + self.event.event_hours
        db.session.commit()
    
    def accept(self, name, hours, comment=None):
        self.status = 'Accepted'
        if(hours == None):
            self.hours_given = self.event.event_hours
        else:
            self.hours_given = hours
        
        if(comment is None):
            self.comments = " "
        else:
            self.comments = comment
            db.session.commit()
        self.decision_student = name
        self.decision_time = datetime.now()
        self.student.current_hours = self.student.current_hours + self.hours_given
        self.student.pending_hours = self.student.pending_hours - self.event.event_hours
        db.session.commit()

    def deny(self, name, comment):
        print(comment)
        self.status = "Denied"
        if(comment is None):
            self.comments = " "
        else:
            self.comments = comment
            db.session.commit()
        self.decision_student = name
        self.decision_time = datetime.now()
        self.student.pending_hours = self.student.pending_hours - self.event.event_hours
        db.session.commit()

    def unregister(self):
        self.status = "Unregistered"
        print(self.event.event_name)
        print(str(self.event.spots_available) +  " is the spots availble")
        if self.event.spots_available is not None:
            self.event.spots_available = self.event.spots_available + 1
        self.student.pending_hours = self.student.pending_hours - self.event.event_hours
        db.session.commit()


class recurring_events(db.Model):
    event_id = db.Column(db.Integer, db.ForeignKey('event_info.event_id'),  primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_info.student_id'), primary_key = True)
    numb_of_hours = db.Column(db.Float())


class announcements(db.Model):
    announcement_id = db.Column(db.Integer, primary_key = True)
    announcement_date_time = db.Column(db.DateTime(timezone= True), default=datetime.utcnow)
    announcement_title = db.Column(db.String(1000))
    announcement = db.Column(db.String(100000))
    file_name = db.Column(db.String(1000), default= None)


