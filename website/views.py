from flask import Flask
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.functions import user
app = Flask(__name__)
from sqlalchemy.orm import session
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.roles import OrderByRole
from website.models import login_details, announcements, event_info, registration, student_info
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_from_directory, abort, copy_current_request_context, current_app
from flask_login import login_required, current_user
import datetime
from . import db
from website.Config import GlobalVariables
from sqlalchemy import asc, desc, func
import os
from flask import current_app
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_wtf import FlaskForm
from website.Config import Config
import re
from sqlalchemy import or_
import sys
from werkzeug.security import generate_password_hash, check_password_hash
import threading
from flask_mail import Message, Mail

views = Blueprint('views', __name__)

app.config.from_object(Config)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config["ALLOWED_FILE_EXTENSIONS"] = ["PNG", "JPG", "JPEG", "GIF", "PDF", "DOC", "TXT", "DOCX"]


def allowed_file(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_FILE_EXTENSIONS"]:
        return True
    else: 
        return False

def announcement_query():
    return announcements.query

class ChoiceForm(FlaskForm):
    opts = QuerySelectField(query_factory=announcement_query, allow_blank=False, get_label='announcement_title', default= lambda: db.session.query(announcements).order_by(announcements.announcement_date_time.desc()).first())

 
@login_required
@views.route('/home', methods = ['GET', 'POST'])
def home(): 
    if request.method == 'POST' and request.form.get('undo') != None:
        print(request.form.get('undo'))


        db.session.query(registration).filter(registration.idreg == int((request.form.get('undo')))).first().undo()
        print(db.session.query(registration).filter(registration.idreg == int((request.form.get('undo')))).first().status)
        return redirect(url_for('views.review'))


    if request.method == 'POST' and request.form.get('reg') != None:
        unregister_obj = db.session.query(registration).filter(registration.idreg == request.form.get('reg').split('/')).first()
        unregister_obj.unregister()
    registered = db.session.query(registration).join(event_info).filter(registration.student_id == current_user.student_id)
    pastevents = registered.filter(event_info.event_time < datetime.datetime.now()).order_by(event_info.event_time.asc())
    for pastevent in pastevents:
        if(pastevent.status == "Registered"):
            pastevent.status = "Waiting"
        elif(pastevent.status == "Unregistered"):
            pastevent.status = "Declined"

    db.session.commit()
    
    pastevent2 = []
    #for x in range(0, 12):
        #ev = pastevents.filter(event_info.event_time >= f'{datetime.datetime.now().year}-{x+1}-01').filter(event_info.event_time < f'{datetime.datetime.now().year}-{x+2}-01').order_by(event_info.event_time).all()
    #ev = pastevents
        #print(ev)
        #pastevent2.append([])
    for y in pastevents:
        pastevent2.append(y)

    #print(pastevent2[7])
    for past in pastevent2:
        print(past.event.event_name)

    registered = registered.filter(registration.status == "Registered") 
    #.filter(event_info.event_time >= datetime.datetime.now()).filter(registration.status == "Registered")  
    registered = registered.order_by(event_info.event_time.asc()) 
    announcement2 = db.session.query(announcements).order_by(announcements.announcement_date_time)
    form = ChoiceForm()
    current_announcement = db.session.query(announcements).order_by(announcements.announcement_date_time.desc()).first()
    if form.validate_on_submit():
        result = re.sub('[^0-9]','', str(form.opts.data))
        chosen = int(result)
        current_announcement = db.session.query(announcements).get(chosen)
        print(current_announcement.announcement_title)
    return render_template("index.html", 
    user = current_user, 
    registered = registered, 
    announcement2 = announcement2, 
    pastevents = pastevent2, 
    now = datetime.datetime.now(), 
    form = form, 
    current_announcement=current_announcement,
    past_decisions = get_past_decisions(current_user)
    )

@login_required
@views.route('/profile')
def profile(): 
     return render_template("profile.html")

@login_required
@views.route('/signup', methods = ['GET','POST']) 
def signup():
    if request.method == "POST":
        register_id = request.form.get("register_button").split('/')
        if(register_id[0] == "register"):
            if hasattr(db.session.query(registration).filter(registration.student_id == current_user.student_id, registration.event_id == register_id[1] ).first(), 'status'):
                db.session.query(registration).filter(registration.student_id == current_user.student_id, registration.event_id == register_id[1] ).first().status = "Registered"
                db.session.commit()
            
            else:
                new_registeration = registration(
                                    status = "Registered" , 
                                    comments = None, time_submitted = datetime.datetime.now(), 
                                    event = db.session.query(event_info).filter(event_info.event_id == register_id[1]).first(),
                                    student = current_user,
                                    decision_student = None
                                    )

                db.session.add(new_registeration)
                db.session.commit()

            update_spots = db.session.query(event_info).filter(event_info.event_id == register_id[1]).first()
            update_spots.spots_available = update_spots.spots_available - 1
            db.session.commit()

            current_user.pending_hours = current_user.pending_hours + update_spots.event_hours
            db.session.commit()
            return redirect(url_for("views.home"))

        else:
            db.session.query(registration).filter(registration.idreg == register_id).first().unregister()

    events1 = db.session.query(event_info)
    #.filter(event_info.event_time >= datetime.datetime.now())
    events1 = events1.order_by(event_info.event_time.asc()) 
    statuses = []
    event2 = []
    for event3 in events1 :

        if (hasattr(db.session.query(registration).filter(registration.student_id == current_user.student_id, registration.event_id == event3.event_id).first(), 'status')):
            if(db.session.query(registration).filter(registration.student_id == current_user.student_id, registration.event_id == event3.event_id).first().status == "Registered"):
                statuses.append(True)
            else:
                statuses.append(False)
        else:
            statuses.append(False)
        event2.append(event3)
        print(statuses)

    return render_template("signup.html", events = event2, statuses = statuses)

@login_required
@views.route('/createannouncement', methods = ['GET', 'POST'])
def createannouncement():
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(current_user.boardMember):
        if request.method == 'POST':
             announcement_title = request.form.get('announcementTitle')
             announcement = request.form.get('summernote')
             if request.files['announcementFile'] != None:
                announcement_file = request.files['announcementFile']
             else: 
                announcement_file = None
             announcement_date = datetime.datetime.now()
             if len(announcement_title) < 1:
                 flash('Announcement title must be greater than 1 character.', category='error')
             elif len(announcement) < 1:
                 flash('Announcement must be greater than 1 character.', category='error')
             elif not allowed_file(announcement_file.filename) and announcement_file.tell() != 0:
                 flash('File extension is not allowed, only JPG, JPEG, PNG, PDF, DOC, DOCX, TXT, and GIF are allowed.', category='error')
             else:
                 if (announcement_file.tell() == 0):
                    announcement_file.filename == None
                 else:         
                  announcement_file.save(os.path.join(basedir, app.config["UPLOAD_FOLDER"], announcement_file.filename))
                  
                
                 filename = announcement_file.filename
                 new_announcement = announcements(announcement_date_time = announcement_date, announcement_title=announcement_title,  file_name = announcement_file.filename, announcement = announcement)
                 db.session.add(new_announcement)
                 db.session.commit()
                 recipient_emails = db.session.query(student_info.email).all()
                 recipient_emails1 =  str(re.sub(r'[()]', '', str(recipient_emails)))
                 recipient_emails2 =  recipient_emails1.replace(',,', '')
                 recipient_emails2 = recipient_emails2.replace("'", '')
                 recipient_emails3 =  recipient_emails2.strip('[]')
                 recipient_emails3 = recipient_emails3[:-1]
                 recipient_list = list(recipient_emails3.split(" "))
                 new_announcement_email = Message(f'''Key Club New Announcement: {announcement_title}''', sender='raymondmoy11@gmail.com', recipients=recipient_list)
                 new_announcement_email.html = f'''<html> <body> {announcement} </body></html>'''
                 new_announcement_email.attach(announcement_file.filename,"application/octet-stream", announcement_file.read())
                 
                 mail = Mail(app)
                 mail.init_app(app)
                 mail.send(new_announcement_email)


                 flash('Announcement sent successfully!', category='success')
        return render_template("createannouncement.html")

    else:
        flash("You cannot view this page", category = "error")
        return redirect(url_for("views.home"))  


@login_required
@views.route('/download/<filename>')
def get_file(filename):
    try:
        return send_from_directory(
            app.config["UPLOAD_FOLDER"], path=filename, as_attachment=True
            )

    except FileNotFoundError:
        abort(404)



@login_required
@views.route('/createevent', methods = ['GET', 'POST'])
def createevent():
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(current_user.boardMember):
        if(request.method == "POST"):
            event_title = request.form.get("event_title")
            event_location = request.form.get("event_location")
            event_hours = request.form.get("event_hours")
            event_dates_info = request.form.get("event_date").split("/")
            event_times_info = request.form.get("event_time").split(":")
            event_date = datetime.datetime(int(event_dates_info[2]), int(event_dates_info[1]), 
            int(event_dates_info[0]), int(event_times_info[0]), int(event_times_info[1]))
            more_info = request.form.get("event_info")
            spots_available = request.form.get("spots_available")
            event_type = request.form.get("event_type")
            if request.files['event_file'] != None:
                event_file = request.files['event_file']
            else: 
                event_file = None
    
            if len(event_title) < 1:
                flash('Event title must be greater than 1 character.', category='error')
            elif len(event_location) < 1:
                flash('Location must be greater than 1 character.', category='error')
            elif not allowed_file(event_file.filename) and event_file.tell() != 0:
                flash('File extension is not allowed, only JPG, JPEG, PNG, PDF, DOC, DOCX, TXT, and GIF are allowed.', category='error')
            else:
                print(event_date)
                print(event_location)
                #if (event_file.tell() == 0):
                    #event_file.filename == None
                #else:
                event_file.save(os.path.join(basedir, app.config["UPLOAD_FOLDER"], event_file.filename))
                
                
                new_event = event_info(event_name = event_title, event_time = event_date, event_hours = event_hours, event_location = event_location,
                more_info = more_info, event_type = event_type, event_reccurent = False, spots_available = spots_available, event_filename = event_file.filename)
                event_filename = event_file.filename
                db.session.add(new_event)
                db.session.commit()
                print(new_event.event_id)
                return redirect(url_for("views.signup"))



        return render_template("createevent.html")
    else:
        flash("You cannot view this page", category = "error")
        return redirect(url_for("views.home"))

@login_required
@views.route('/review', methods = ['GET', 'POST'])
def review():
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(request.method == "POST"):
        val = int(request.form.get("reviewbutton"))
        return redirect(url_for("views.eventpage", id = val))
    if(current_user.boardMember):
        events = db.session.query(event_info).filter(event_info.event_time < datetime.datetime.now()).order_by(event_info.event_time.asc()).all()
        for r in events:
            print(len(r.event_registered))

        return render_template("review.html", events = events)
        
    else:
        flash("You cannot view this page", category = "error")
        return redirect(url_for("views.home"))



@login_required
@views.route('/eventpage/<id>', methods = ['GET', 'POST'])
def eventpage(id):
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    id = id
    if(id == None):
        print("Cannot execute Event Page")
    else:
        print(id + " ID is the ID")
        #Add if statement for id number and redirect to home
        if(request.method == 'POST'):
            decision_information = request.form.get("approve").split("/")
            string = decision_information[1]
            print(string)
            register_object = db.session.query(registration).filter(registration.idreg == string).first()
            if(decision_information[0] == "approve"):
                register_object.accept(name = current_user.first_name)
            elif decision_information[0] == "deny":
                register_object.deny()
        event = db.session.query(event_info).filter(event_info.event_id == id).first()
        print(event.event_name)
        return render_template("cannedfooddonation.html", event = event )

@login_required
@views.route('/admin', methods = ['GET', 'POST'])
def admin():
    f = GlobalVariables()
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(f.admin_access == current_user.student_id):
        return redirect(url_for('views.adminaccept'))
    if(request.method == "POST"):
        if(request.form.get('pass') != None and len(request.form.get('pass')) != 0):
            admin = db.session.query(login_details).filter(login_details.id == "001").first()
            print(admin.password)
            if check_password_hash(admin.password, request.form.get('pass')):
                flash(message='Password is correct', category='sucess')
                GlobalVariables.admin_access = current_user.student_id
                return redirect(url_for('views.adminaccept'))
            else:
                flash(message='Password is incorrect', category='error') 
        elif(request.form.get('reset') != None):
            admin_obj = db.session.query(login_details).filter(login_details.id == "001").first()
            admin_obj.password = generate_password_hash(app.config['ADMIN_PASSWORD'])
            db.session.commit()
            flash(message="Your password has been reset", category="success")  
    return render_template('admin.html')

@login_required
@views.route('/adminaccept', methods = ['GET', 'POST'])
def adminaccept():
    g = GlobalVariables()
    if(g.admin_access != current_user.student_id):
        return redirect(url_for('views.home'))
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(request.method == "POST"):
        if(request.form.get('email') != None):
             email = request.form.get('email')
             print(email)
             person = db.session.query(student_info).filter(student_info.email == email).first()
             if(person is None):
                 flash(message="No email found", category="error")
             else:
                 person.boardMember = True
                 db.session.commit()
                 flash(message= f"{person.first_name} {person.last_name} has become a board member", category="success")
        elif(request.form.get('remove') != None):
            stu_id = int(request.form.get('remove'))
            person = db.session.query(student_info).filter(student_info.student_id == stu_id).first()
            person.boardMember = False
            db.session.commit()
            flash(message= f"{person.first_name} {person.last_name} is not a board member anymore", category = "success")
        elif(request.form.get('currentpassword') != None):
            current_password = request.form.get('currentpassword')
            new_password = request.form.get('newpassword')
            confirm_new_password = request.form.get('confirmnewpassword')
            admin_obj = db.session.query(login_details).filter(login_details.id == "001").first()
            if check_password_hash(admin_obj.password, current_password) == False:
                flash(message="Current Password Is incorrect", category="error")
            elif(new_password != confirm_new_password):
                flash(message="New passwords do not match", category="error")
            else:
                admin_obj.password = generate_password_hash(new_password)
                db.session.commit()
                flash(message="Your password has been changed", category="success")

            

            



        


        
    


        
    boardMembers = db.session.query(student_info).filter(student_info.boardMember == True).all()
    return render_template('adminaccept.html', boardMembers = boardMembers)




def unregister(register_id):
    status2 = db.session.query(registration).filter(registration.student_id == current_user.student_id, registration.event_id == register_id[1]).first()
    status2.status = "Unregistered"
    update_spots = db.session.query(event_info).filter(event_info.event_id == register_id[1]).first()
    update_spots.spots_available = update_spots.spots_available + 1
    current_user.pending_hours = current_user.pending_hours - update_spots.event_hours
    db.session.commit()


def get_past_decisions(user1):
    list = db.session.query(registration).filter(or_(registration.status == "Accepted", registration.status == "Denied")).order_by(registration.decision_time.desc()).all()
    return list

from flask import Flask
from sqlalchemy.sql.expression import false, true
from sqlalchemy.sql.functions import user
app = Flask(__name__)
from sqlalchemy.orm import session
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.roles import OrderByRole
from website.models import login_details, announcements, event_info, registration, student_info
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_from_directory, abort
from flask_login import login_required, current_user
import datetime
from . import db
from sqlalchemy import asc, desc, func
import os
from flask import current_app
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_wtf import FlaskForm
from website.Config import Config
import re
from sqlalchemy import or_, extract
import sys
from werkzeug.security import generate_password_hash, check_password_hash
import pytz


views = Blueprint('views', __name__)

app.config.from_object(Config)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config["UPLOAD_FOLDER"] = "./uploads"
app.config["ALLOWED_FILE_EXTENSIONS"] = ["PNG", "JPG", "JPEG", "GIF", "PDF", "DOC", "TXT", "DOCX"]


def allowed_file(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_FILE_EXTENSIONS"]:
        return True
    else: 
        return False

def announcement_query():
    return announcements.query

class ChoiceForm(FlaskForm):
    opts = QuerySelectField(query_factory=announcement_query, allow_blank=False, get_label='announcement_title', default= lambda: db.session.query(announcements).order_by(announcements.announcement_date_time.desc()).first())

 
@login_required
@views.route('/home', methods = ['GET', 'POST'])
def home(): 
    if request.method == 'POST' and request.form.get('undo') != None:
        print(request.form.get('undo'))


        db.session.query(registration).filter(registration.idreg == int((request.form.get('undo')))).first().undo()
        print(db.session.query(registration).filter(registration.idreg == int((request.form.get('undo')))).first().status)
        return redirect(url_for('views.review'))




    if request.method == 'POST' and request.form.get('reg') != None:
        unregister_obj = db.session.query(registration).filter(registration.idreg == request.form.get('reg').split('/')[1]).first()
        unregister_obj.unregister()
    print(type(current_user))
    timez = pytz.timezone('US/Eastern')
    registered = db.session.query(registration).join(event_info).filter(registration.student_id == current_user.student_id)
    pastevents = registered.filter(event_info.event_time < datetime.datetime.now(timez)).order_by(event_info.event_time.desc())
    for pastevent in pastevents:
        if(pastevent.status == "Registered"):
            pastevent.status = "Waiting"
        elif(pastevent.status == "Unregistered"):
            pastevent.status = "Declined"

    db.session.commit()
    
    pastevent2 = []


    #for x in range(0, 12):
        #ev = pastevents.filter(event_info.event_time >= f'{datetime.datetime.now().year}-{x+1}-01').filter(event_info.event_time < f'{datetime.datetime.now().year}-{x+2}-01').order_by(event_info.event_time).all()
    #ev = pastevents
        #print(ev)
        #pastevent2.append([])
        #Note, do not need any of this. Just write filter datetimedatetime.now()

    for x in range(0,13):
        pastevent2.append([])
       # pastevents = pastevents.filter(event_info.event_time <  datetime.datetime.now())
    for pastevmonths in range(1,13):
        monthpastevent = pastevents.filter(extract('month', event_info.event_time) == pastevmonths).order_by(event_info.event_time.desc()).all()
        if(monthpastevent is not None):
            pastevent2[pastevmonths] = monthpastevent

    #print(pastevent2[7])
 
    registered = registered.filter(registration.status == "Registered").filter(event_info.event_time >= datetime.datetime.now(timez))
    registered = registered.order_by(event_info.event_time.asc()) 
    announcement2 = db.session.query(announcements).order_by(announcements.announcement_date_time)
    form = ChoiceForm()
    current_announcement = db.session.query(announcements).order_by(announcements.announcement_date_time.desc()).first()
    if form.validate_on_submit():
        result = re.sub('[^0-9]','', str(form.opts.data))
        chosen = int(result)
        current_announcement = db.session.query(announcements).get(chosen)
        print(current_announcement.announcement_title)
    return render_template("index.html", 
    user = current_user, 
    registered = registered, 
    announcement2 = announcement2, 
    pastevents = pastevent2, 
    now = datetime.datetime.now(timez), 
    form = form, 
    current_announcement=current_announcement,
    past_decisions = get_past_decisions(current_user)
    )

@login_required
@views.route('/profile', methods = ['GET', 'POST'])
def profile():
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(request.method == "POST"):
        if(request.form.get('changeemail') is not None or request.form.get('changeemail') != ""):
            if(len(request.form.get('changeemail') ) < 3):
                flash(message="Email is too short", category="error")
            else:
                current_user.email = request.form.get('changeemail')
                db.session.commit()
                flash(message="Email changed successfully", category="success")

        checkvalues = request.form.getlist('checkbox')
        for x in range(1,4):
            if(x==1):
                if("1" in checkvalues):
                    current_user.announcementnotifications = True
                else:
                    current_user.announcementnotifications = False
            elif(x == 2):
                if("2" in checkvalues):
                    current_user.approvalnotifications = True
                else:
                    current_user.approvalnotifications = False
            elif(x==3):
                if("3" in checkvalues):
                    current_user.eventnotifcations = True
                else:
                    current_user.eventnotifications = False

        print(current_user.announcementnotifications) 
        print(current_user.approvalnotifications)
        print(current_user.eventnotifcations)
        db.session.commit()  
    student = current_user

    return render_template("profile.html", student = student)

@login_required
@views.route('/signup', methods = ['GET','POST']) 
def signup():
    timez = pytz.timezone('US/Eastern')
    if request.method == "POST":
        register_id = request.form.get("register_button").split('/')
        if(register_id[0] == "register"):
            if hasattr(db.session.query(registration).filter(registration.student_id == current_user.student_id, registration.event_id == register_id[1] ).first(), 'status'):
                db.session.query(registration).filter(registration.student_id == current_user.student_id, registration.event_id == register_id[1] ).first().status = "Registered"
                db.session.commit()
            else:
                new_registeration = registration(
                                    status = "Registered" , 
                                    comments = None, time_submitted = datetime.datetime.now(timez), 
                                    event = db.session.query(event_info).filter(event_info.event_id == register_id[1]).first(),
                                    student = current_user,
                                    decision_student = None
                                    )

                db.session.add(new_registeration)
                db.session.commit()
            update_spots = db.session.query(event_info).filter(event_info.event_id == register_id[1]).first()
            if(update_spots.spots_available is not None):
                update_spots.spots_available = update_spots.spots_available - 1
            db.session.commit()

            current_user.pending_hours = current_user.pending_hours + update_spots.event_hours
            db.session.commit()
            return redirect(url_for("views.home"))

        else:
            db.session.query(registration).filter(registration.idreg == register_id[1]).first().unregister()

    events1 = db.session.query(event_info).filter(event_info.event_time >= datetime.datetime.now(timez))
    events1 = events1.order_by(event_info.event_time.asc()) 
    statuses = []
    event2 = []
    for event3 in events1 :

        if (hasattr(db.session.query(registration).filter(registration.student_id == current_user.student_id, registration.event_id == event3.event_id).first(), 'status')):
            if(db.session.query(registration).filter(registration.student_id == current_user.student_id, registration.event_id == event3.event_id).first().status == "Registered"):
                statuses.append(True)
            else:
                statuses.append(False)
        else:
            statuses.append(False)
        event2.append(event3)
        print(statuses)

    return render_template("signup.html", events = event2, statuses = statuses)

@login_required
@views.route('/createannouncement', methods = ['GET', 'POST'])
def createannouncement():
    timez = pytz.timezone('US/Eastern')
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(current_user.boardMember):
        if request.method == 'POST':
             announcement_title = request.form.get('announcementTitle')
             announcement = request.form.get('summernote')
             if request.files['announcementFile'] != None:
                announcement_file = request.files['announcementFile']
             else: 
                announcement_file = None
             announcement_date = datetime.datetime.now(timez)
             if len(announcement_title) < 1:
                 flash('Announcement title must be greater than 1 character.', category='error')
             elif len(announcement) < 1:
                 flash('Announcement must be greater than 1 character.', category='error')
             elif not allowed_file(announcement_file.filename) and announcement_file.filename != '':
                 flash('File extension is not allowed, only JPG, JPEG, PNG, PDF, DOC, DOCX, TXT, and GIF are allowed.', category='error')
             else:
                if(announcement_file.filename != ''):
                    announcement_file.save(os.path.join(basedir, app.config["UPLOAD_FOLDER"], announcement_file.filename))
                    filename = announcement_file.filename
                new_announcement = announcements(announcement_date_time = announcement_date, announcement_title=announcement_title,  file_name = announcement_file.filename, announcement = announcement)
                db.session.add(new_announcement)
                db.session.commit()    
                flash('Announcement sent successfully!', category='success')
              #   people = db.session.query(student_info).filter(student_info.announcementnotifications == True).all()
              #   for person in people:
               #      person.sendemail(message="New Announcement Posted", 
                     
                #     body = f'''

#Hello, 


#A new announcement has been posted called {new_announcement.announcement_title}

 #                    ''')
                     
        return render_template("createannouncement.html")

   # else:
    #    flash("You cannot view this page", category = "error")
     #   return redirect(url_for("views.home"))  


@login_required
@views.route('/download/<filename>')
def get_file(filename):
    try:
        return send_from_directory(
            app.config["UPLOAD_FOLDER"], path=filename, as_attachment=True
            )

    except FileNotFoundError:
        abort(404)



@login_required
@views.route('/createevent', methods = ['GET', 'POST'])
def createevent():
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(current_user.boardMember):
        if(request.method == "POST"):
            event_title = request.form.get("event_title")
            event_location = request.form.get("event_location")
            if request.form.get("customhours") is None:
                event_hours = request.form.get("event_hours")
            else:
                event_hours = 0
            event_dates_info = request.form.get("event_date").split("/")
            event_times_info = request.form.get("event_time").split(":")
            event_date = datetime.datetime(int(event_dates_info[2]), int(event_dates_info[1]), 
            int(event_dates_info[0]), int(event_times_info[0]), int(event_times_info[1]))
            more_info = request.form.get("event_info")
            if len(request.form.getlist('nullspots')) == 0:
                spots_available = request.form.get("spots_available")
            else:
                spots_available = None
            event_type = request.form.get("event_type")
            if request.files['event_file'] != None:
                event_file = request.files['event_file']
            else: 
                event_file = None
    
            if len(event_title) < 1:
                flash('Event title must be greater than 1 character.', category='error')
            elif len(event_location) < 1:
                flash('Location must be greater than 1 character.', category='error')
            elif not allowed_file(event_file.filename) and len(event_file.filename) != 0:
                flash('File extension is not allowed, only JPG, JPEG, PNG, PDF, DOC, DOCX, TXT, and GIF are allowed.', category='error')
            else:
                print(event_date)
                print(event_location)
                if (len(event_file.filename) != 0):
                    event_file.save(os.path.join(basedir, app.config["UPLOAD_FOLDER"], event_file.filename))
                
                
                new_event = event_info(event_name = event_title, event_time = event_date, event_hours = event_hours, event_location = event_location,
                more_info = more_info, event_type = event_type, event_reccurent = False, spots_available = spots_available, event_filename = event_file.filename)
                event_filename = event_file.filename
                db.session.add(new_event)
                db.session.commit()
                print(new_event.event_id)
                return redirect(url_for("views.signup"))



        return render_template("createevent.html")
    else:
        flash("You cannot view this page", category = "error")
        return redirect(url_for("views.home"))

@login_required
@views.route('/review', methods = ['GET', 'POST'])
def review():
    timez = pytz.timezone('US/Eastern')
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(request.method == "POST"):
        val = int(request.form.get("reviewbutton"))
        return redirect(url_for("views.eventpage", id = val))
    if(current_user.boardMember):
        events = db.session.query(event_info).filter(event_info.event_time < datetime.datetime.now(timez)).order_by(event_info.event_time.asc()).all()
        for r in events:
            print(len(r.event_registered))

        return render_template("review.html", events = events)
        
    else:
        flash("You cannot view this page", category = "error")
        return redirect(url_for("views.home"))



@login_required
@views.route('/eventpage/<id>', methods = ['GET', 'POST'])
def eventpage(id):
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    id = id
    if(id == None):
        print("Cannot execute Event Page")
    else:
        print(id + " ID is the ID")
        #Add if statement for id number and redirect to home
        if(request.method == 'POST'):
            decision_information = request.form.get("approve").split("/")
            string = decision_information[1]
            print(string)
            register_object = db.session.query(registration).filter(registration.idreg == string).first()
            comment = request.form.get("comment")
            hours = request.form.get("hoursgiven")
            if(decision_information[0] == "approve"):
                register_object.accept(name = current_user.first_name, hours = hours, comment=comment)
            elif decision_information[0] == "deny":
                register_object.deny(name = current_user.first_name, comment = comment)
        event = db.session.query(event_info).filter(event_info.event_id == id).first()
        if(event is None):
            abort(404)
        print(event.event_name)
        return render_template("cannedfooddonation.html", event = event )

@login_required
@views.route('/admin', methods = ['GET', 'POST'])
def admin():
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(request.method == "POST"):
        if(request.form.get('pass') != None and len(request.form.get('pass')) != 0):
            admin = db.session.query(login_details).filter(login_details.id == "001").first()
            print(admin.password)
            if check_password_hash(admin.password, request.form.get('pass')):
                flash(message='Password is correct', category='sucess')
                return redirect(url_for('views.adminaccept', key = generate_password_hash("egdhoisatuq59873609taldhgid", method = "sha256")))
            else:
                flash(message='Password is incorrect', category='error') 
        elif(request.form.get('reset') != None):
            admin_obj = db.session.query(login_details).filter(login_details.id == "001").first()
            admin_obj.password = generate_password_hash(app.config['ADMIN_PASSWORD'])
            db.session.commit()
            flash(message="Your password has been reset", category="success")  
    return render_template('admin.html')

@login_required
@views.route('/adminaccept<key>', methods = ['GET', 'POST'])
def adminaccept(key):
    if(key == False):
        return redirect(url_for('auth.login'))
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(request.method == "POST"):
        if(request.form.get('email') != None):
             email = request.form.get('email')
             print(email)
             person = db.session.query(student_info).filter(student_info.email == email).first()
             if(person is None):
                 flash(message="No email found", category="error")
             else:
                 person.boardMember = True
                 db.session.commit()
                 flash(message= f"{person.first_name} {person.last_name} has become a board member", category="success")
        elif(request.form.get('remove') != None):
            stu_id = int(request.form.get('remove'))
            person = db.session.query(student_info).filter(student_info.student_id == stu_id).first()
            person.boardMember = False
            db.session.commit()
            flash(message= f"{person.first_name} {person.last_name} is not a board member anymore", category = "success")
        elif(request.form.get('currentpassword') != None):
            current_password = request.form.get('currentpassword')
            new_password = request.form.get('newpassword')
            confirm_new_password = request.form.get('confirmnewpassword')
            admin_obj = db.session.query(login_details).filter(login_details.id == "001").first()
            if check_password_hash(admin_obj.password, current_password) == False:
                flash(message="Current Password Is incorrect", category="error")
            elif(new_password != confirm_new_password):
                flash(message="New passwords do not match", category="error")
            else:
                admin_obj.password = generate_password_hash(new_password)
                db.session.commit()
                flash(message="Your password has been changed", category="success")

        
    boardMembers = db.session.query(student_info).filter(student_info.boardMember == True).all()
    return render_template('adminaccept.html', boardMembers = boardMembers)




def unregister(register_id):
    status2 = db.session.query(registration).filter(registration.student_id == current_user.student_id, registration.event_id == register_id[1]).first()
    status2.status = "Unregistered"
    update_spots = db.session.query(event_info).filter(event_info.event_id == register_id[1]).first()
    update_spots.spots_available = update_spots.spots_available + 1
    current_user.pending_hours = current_user.pending_hours - update_spots.event_hours
    db.session.commit()


def get_past_decisions(user1):
    pastdecisions = []
    query = db.session.query(registration).filter(or_(registration.status == "Accepted", registration.status == "Denied")).order_by(registration.decision_time.desc())
    for x in range(0,13):
        pastdecisions.append([])
    for pastevmonths in range(1,13):
        monthpastevent = query.filter(extract('month', registration.decision_time) == pastevmonths).order_by(registration.decision_time.desc()).all()
        if(monthpastevent is not None):
            pastdecisions[pastevmonths] = monthpastevent
    return pastdecisions



=======
from flask import Flask
from sqlalchemy.sql.expression import false, true
from sqlalchemy.sql.functions import user
app = Flask(__name__)
from sqlalchemy.orm import session
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.roles import OrderByRole
from website.models import login_details, announcements, event_info, registration, student_info
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_from_directory, abort
from flask_login import login_required, current_user
import datetime
from . import db
from sqlalchemy import asc, desc, func
import os
from flask import current_app
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_wtf import FlaskForm
from website.Config import Config
import re
from sqlalchemy import or_, extract
import sys
from werkzeug.security import generate_password_hash, check_password_hash
import pytz


views = Blueprint('views', __name__)

app.config.from_object(Config)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config["UPLOAD_FOLDER"] = "./uploads"
app.config["ALLOWED_FILE_EXTENSIONS"] = ["PNG", "JPG", "JPEG", "GIF", "PDF", "DOC", "TXT", "DOCX"]


def allowed_file(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_FILE_EXTENSIONS"]:
        return True
    else: 
        return False

def announcement_query():
    return announcements.query

class ChoiceForm(FlaskForm):
    opts = QuerySelectField(query_factory=announcement_query, allow_blank=False, get_label='announcement_title', default= lambda: db.session.query(announcements).order_by(announcements.announcement_date_time.desc()).first())

 
@login_required
@views.route('/home', methods = ['GET', 'POST'])
def home(): 
    if request.method == 'POST' and request.form.get('undo') != None:
        print(request.form.get('undo'))


        db.session.query(registration).filter(registration.idreg == int((request.form.get('undo')))).first().undo()
        print(db.session.query(registration).filter(registration.idreg == int((request.form.get('undo')))).first().status)
        return redirect(url_for('views.review'))




    if request.method == 'POST' and request.form.get('reg') != None:
        unregister_obj = db.session.query(registration).filter(registration.idreg == request.form.get('reg').split('/')[1]).first()
        unregister_obj.unregister()
    print(type(current_user))
    timez = pytz.timezone('US/Eastern')
    registered = db.session.query(registration).join(event_info).filter(registration.student_id == current_user.student_id)
    pastevents = registered.filter(event_info.event_time < datetime.datetime.now(timez)).order_by(event_info.event_time.desc())
    for pastevent in pastevents:
        if(pastevent.status == "Registered"):
            pastevent.status = "Waiting"
        elif(pastevent.status == "Unregistered"):
            pastevent.status = "Declined"

    db.session.commit()
    
    pastevent2 = []


    #for x in range(0, 12):
        #ev = pastevents.filter(event_info.event_time >= f'{datetime.datetime.now().year}-{x+1}-01').filter(event_info.event_time < f'{datetime.datetime.now().year}-{x+2}-01').order_by(event_info.event_time).all()
    #ev = pastevents
        #print(ev)
        #pastevent2.append([])
        #Note, do not need any of this. Just write filter datetimedatetime.now()

    for x in range(0,13):
        pastevent2.append([])
       # pastevents = pastevents.filter(event_info.event_time <  datetime.datetime.now())
    for pastevmonths in range(1,13):
        monthpastevent = pastevents.filter(extract('month', event_info.event_time) == pastevmonths).order_by(event_info.event_time.desc()).all()
        if(monthpastevent is not None):
            pastevent2[pastevmonths] = monthpastevent

    #print(pastevent2[7])
 
    registered = registered.filter(registration.status == "Registered").filter(event_info.event_time >= datetime.datetime.now(timez))
    registered = registered.order_by(event_info.event_time.asc()) 
    announcement2 = db.session.query(announcements).order_by(announcements.announcement_date_time)
    form = ChoiceForm()
    current_announcement = db.session.query(announcements).order_by(announcements.announcement_date_time.desc()).first()
    if form.validate_on_submit():
        result = re.sub('[^0-9]','', str(form.opts.data))
        chosen = int(result)
        current_announcement = db.session.query(announcements).get(chosen)
        print(current_announcement.announcement_title)
    return render_template("index.html", 
    user = current_user, 
    registered = registered, 
    announcement2 = announcement2, 
    pastevents = pastevent2, 
    now = datetime.datetime.now(timez), 
    form = form, 
    current_announcement=current_announcement,
    past_decisions = get_past_decisions(current_user)
    )

@login_required
@views.route('/profile', methods = ['GET', 'POST'])
def profile():
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(request.method == "POST"):
        if(request.form.get('changeemail') is not None or request.form.get('changeemail') != ""):
            if(len(request.form.get('changeemail') ) < 3):
                flash(message="Email is too short", category="error")
            else:
                current_user.email = request.form.get('changeemail')
                db.session.commit()
                flash(message="Email changed successfully", category="success")

        checkvalues = request.form.getlist('checkbox')
        for x in range(1,4):
            if(x==1):
                if("1" in checkvalues):
                    current_user.announcementnotifications = True
                else:
                    current_user.announcementnotifications = False
            elif(x == 2):
                if("2" in checkvalues):
                    current_user.approvalnotifications = True
                else:
                    current_user.approvalnotifications = False
            elif(x==3):
                if("3" in checkvalues):
                    current_user.eventnotifcations = True
                else:
                    current_user.eventnotifications = False

        print(current_user.announcementnotifications) 
        print(current_user.approvalnotifications)
        print(current_user.eventnotifcations)
        db.session.commit()  
    student = current_user

    return render_template("profile.html", student = student)

@login_required
@views.route('/signup', methods = ['GET','POST']) 
def signup():
    timez = pytz.timezone('US/Eastern')
    if request.method == "POST":
        register_id = request.form.get("register_button").split('/')
        if(register_id[0] == "register"):
            if hasattr(db.session.query(registration).filter(registration.student_id == current_user.student_id, registration.event_id == register_id[1] ).first(), 'status'):
                db.session.query(registration).filter(registration.student_id == current_user.student_id, registration.event_id == register_id[1] ).first().status = "Registered"
                db.session.commit()
            else:
                new_registeration = registration(
                                    status = "Registered" , 
                                    comments = None, time_submitted = datetime.datetime.now(timez), 
                                    event = db.session.query(event_info).filter(event_info.event_id == register_id[1]).first(),
                                    student = current_user,
                                    decision_student = None
                                    )

                db.session.add(new_registeration)
                db.session.commit()
            update_spots = db.session.query(event_info).filter(event_info.event_id == register_id[1]).first()
            if(update_spots.spots_available is not None):
                update_spots.spots_available = update_spots.spots_available - 1
            db.session.commit()

            current_user.pending_hours = current_user.pending_hours + update_spots.event_hours
            db.session.commit()
            return redirect(url_for("views.home"))

        else:
            db.session.query(registration).filter(registration.idreg == register_id[1]).first().unregister()

    events1 = db.session.query(event_info).filter(event_info.event_time >= datetime.datetime.now(timez))
    events1 = events1.order_by(event_info.event_time.asc()) 
    statuses = []
    event2 = []
    for event3 in events1 :

        if (hasattr(db.session.query(registration).filter(registration.student_id == current_user.student_id, registration.event_id == event3.event_id).first(), 'status')):
            if(db.session.query(registration).filter(registration.student_id == current_user.student_id, registration.event_id == event3.event_id).first().status == "Registered"):
                statuses.append(True)
            else:
                statuses.append(False)
        else:
            statuses.append(False)
        event2.append(event3)
        print(statuses)

    return render_template("signup.html", events = event2, statuses = statuses)

@login_required
@views.route('/createannouncement', methods = ['GET', 'POST'])
def createannouncement():
    timez = pytz.timezone('US/Eastern')
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(current_user.boardMember):
        if request.method == 'POST':
             announcement_title = request.form.get('announcementTitle')
             announcement = request.form.get('summernote')
             if request.files['announcementFile'] != None:
                announcement_file = request.files['announcementFile']
             else: 
                announcement_file = None
             announcement_date = datetime.datetime.now(timez)
             if len(announcement_title) < 1:
                 flash('Announcement title must be greater than 1 character.', category='error')
             elif len(announcement) < 1:
                 flash('Announcement must be greater than 1 character.', category='error')
             elif not allowed_file(announcement_file.filename) and announcement_file.tell() != 0:
                 flash('File extension is not allowed, only JPG, JPEG, PNG, PDF, DOC, DOCX, TXT, and GIF are allowed.', category='error')
             else:
                # if (announcement_file.tell() == 0):
                 #   announcement_file.filename == None
                # else:
                 announcement_file.save(os.path.join(basedir, app.config["UPLOAD_FOLDER"], announcement_file.filename))
                 filename = announcement_file.filename
                 new_announcement = announcements(announcement_date_time = announcement_date, announcement_title=announcement_title,  file_name = announcement_file.filename, announcement = announcement)
                 db.session.add(new_announcement)
                 db.session.commit()    
                 flash('Announcement sent successfully!', category='success')
              #   people = db.session.query(student_info).filter(student_info.announcementnotifications == True).all()
              #   for person in people:
               #      person.sendemail(message="New Announcement Posted", 
                     
                #     body = f'''

#Hello, 


#A new announcement has been posted called {new_announcement.announcement_title}

 #                    ''')
                     
        return render_template("createannouncement.html")

   # else:
    #    flash("You cannot view this page", category = "error")
     #   return redirect(url_for("views.home"))  


@login_required
@views.route('/download/<filename>')
def get_file(filename):
    try:
        return send_from_directory(
            app.config["UPLOAD_FOLDER"], path=filename, as_attachment=True
            )

    except FileNotFoundError:
        abort(404)



@login_required
@views.route('/createevent', methods = ['GET', 'POST'])
def createevent():
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(current_user.boardMember):
        if(request.method == "POST"):
            event_title = request.form.get("event_title")
            event_location = request.form.get("event_location")
            if request.form.get("customhours") is None:
                event_hours = request.form.get("event_hours")
            else:
                event_hours = 0
            event_dates_info = request.form.get("event_date").split("/")
            event_times_info = request.form.get("event_time").split(":")
            event_date = datetime.datetime(int(event_dates_info[2]), int(event_dates_info[1]), 
            int(event_dates_info[0]), int(event_times_info[0]), int(event_times_info[1]))
            more_info = request.form.get("event_info")
            if len(request.form.getlist('nullspots')) == 0:
                spots_available = request.form.get("spots_available")
            else:
                spots_available = None
            event_type = request.form.get("event_type")
            if request.files['event_file'] != None:
                event_file = request.files['event_file']
            else: 
                event_file = None
    
            if len(event_title) < 1:
                flash('Event title must be greater than 1 character.', category='error')
            elif len(event_location) < 1:
                flash('Location must be greater than 1 character.', category='error')
            elif not allowed_file(event_file.filename) and event_file.tell() != 0:
                flash('File extension is not allowed, only JPG, JPEG, PNG, PDF, DOC, DOCX, TXT, and GIF are allowed.', category='error')
            else:
                print(event_date)
                print(event_location)
               # if (event_file.tell() == 0):
                #    event_file.filename == None
               # else:
                event_file.save(os.path.join(basedir, app.config["UPLOAD_FOLDER"], event_file.filename))
                
                
                new_event = event_info(event_name = event_title, event_time = event_date, event_hours = event_hours, event_location = event_location,
                more_info = more_info, event_type = event_type, event_reccurent = False, spots_available = spots_available, event_filename = event_file.filename)
                event_filename = event_file.filename
                db.session.add(new_event)
                db.session.commit()
                print(new_event.event_id)
                return redirect(url_for("views.signup"))



        return render_template("createevent.html")
    else:
        flash("You cannot view this page", category = "error")
        return redirect(url_for("views.home"))

@login_required
@views.route('/review', methods = ['GET', 'POST'])
def review():
    timez = pytz.timezone('US/Eastern')
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(request.method == "POST"):
        val = int(request.form.get("reviewbutton"))
        return redirect(url_for("views.eventpage", id = val))
    if(current_user.boardMember):
        events = db.session.query(event_info).filter(event_info.event_time < datetime.datetime.now(timez)).order_by(event_info.event_time.asc()).all()
        for r in events:
            print(len(r.event_registered))

        return render_template("review.html", events = events)
        
    else:
        flash("You cannot view this page", category = "error")
        return redirect(url_for("views.home"))



@login_required
@views.route('/eventpage/<id>', methods = ['GET', 'POST'])
def eventpage(id):
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    id = id
    if(id == None):
        print("Cannot execute Event Page")
    else:
        print(id + " ID is the ID")
        #Add if statement for id number and redirect to home
        if(request.method == 'POST'):
            decision_information = request.form.get("approve").split("/")
            string = decision_information[1]
            print(string)
            register_object = db.session.query(registration).filter(registration.idreg == string).first()
            comment = request.form.get("comment")
            hours = request.form.get("hoursgiven")
            if(decision_information[0] == "approve"):
                register_object.accept(name = current_user.first_name, hours = hours, comment=comment)
            elif decision_information[0] == "deny":
                register_object.deny(name = current_user.first_name, comment = comment)
        event = db.session.query(event_info).filter(event_info.event_id == id).first()
        if(event is None):
            abort(404)
        print(event.event_name)
        return render_template("cannedfooddonation.html", event = event )

@login_required
@views.route('/admin', methods = ['GET', 'POST'])
def admin():
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(request.method == "POST"):
        if(request.form.get('pass') != None and len(request.form.get('pass')) != 0):
            admin = db.session.query(login_details).filter(login_details.id == "001").first()
            print(admin.password)
            if check_password_hash(admin.password, request.form.get('pass')):
                flash(message='Password is correct', category='sucess')
                return redirect(url_for('views.adminaccept', key = generate_password_hash("egdhoisatuq59873609taldhgid", method = "sha256")))
            else:
                flash(message='Password is incorrect', category='error') 
        elif(request.form.get('reset') != None):
            admin_obj = db.session.query(login_details).filter(login_details.id == "001").first()
            admin_obj.password = generate_password_hash(app.config['ADMIN_PASSWORD'])
            db.session.commit()
            flash(message="Your password has been reset", category="success")  
    return render_template('admin.html')

@login_required
@views.route('/adminaccept<key>', methods = ['GET', 'POST'])
def adminaccept(key):
    if(key == False):
        return redirect(url_for('auth.login'))
    if(current_user.is_authenticated == False):
        return redirect(url_for('auth.login'))
    if(request.method == "POST"):
        if(request.form.get('email') != None):
             email = request.form.get('email')
             print(email)
             person = db.session.query(student_info).filter(student_info.email == email).first()
             if(person is None):
                 flash(message="No email found", category="error")
             else:
                 person.boardMember = True
                 db.session.commit()
                 flash(message= f"{person.first_name} {person.last_name} has become a board member", category="success")
        elif(request.form.get('remove') != None):
            stu_id = int(request.form.get('remove'))
            person = db.session.query(student_info).filter(student_info.student_id == stu_id).first()
            person.boardMember = False
            db.session.commit()
            flash(message= f"{person.first_name} {person.last_name} is not a board member anymore", category = "success")
        elif(request.form.get('currentpassword') != None):
            current_password = request.form.get('currentpassword')
            new_password = request.form.get('newpassword')
            confirm_new_password = request.form.get('confirmnewpassword')
            admin_obj = db.session.query(login_details).filter(login_details.id == "001").first()
            if check_password_hash(admin_obj.password, current_password) == False:
                flash(message="Current Password Is incorrect", category="error")
            elif(new_password != confirm_new_password):
                flash(message="New passwords do not match", category="error")
            else:
                admin_obj.password = generate_password_hash(new_password)
                db.session.commit()
                flash(message="Your password has been changed", category="success")

        
    boardMembers = db.session.query(student_info).filter(student_info.boardMember == True).all()
    return render_template('adminaccept.html', boardMembers = boardMembers)




def unregister(register_id):
    status2 = db.session.query(registration).filter(registration.student_id == current_user.student_id, registration.event_id == register_id[1]).first()
    status2.status = "Unregistered"
    update_spots = db.session.query(event_info).filter(event_info.event_id == register_id[1]).first()
    update_spots.spots_available = update_spots.spots_available + 1
    current_user.pending_hours = current_user.pending_hours - update_spots.event_hours
    db.session.commit()


def get_past_decisions(user1):
    pastdecisions = []
    query = db.session.query(registration).filter(or_(registration.status == "Accepted", registration.status == "Denied")).order_by(registration.decision_time.desc())
    for x in range(0,13):
        pastdecisions.append([])
    for pastevmonths in range(1,13):
        monthpastevent = query.filter(extract('month', registration.decision_time) == pastevmonths).order_by(registration.decision_time.desc()).all()
        if(monthpastevent is not None):
            pastdecisions[pastevmonths] = monthpastevent
    return pastdecisions


>>>>>>> d5fe0ddbf29391e3c595eb1a251a52637a067833
