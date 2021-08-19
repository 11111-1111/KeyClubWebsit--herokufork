from sqlalchemy.orm import session
from sqlalchemy.sql.roles import OrderByRole
from website.models import announcements, event_info, registration, student_info
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_from_directory, abort
from flask_login import login_required, current_user
import datetime
from . import db
from sqlalchemy import asc, desc, func
import os
from flask import current_app
from flask import Flask

views = Blueprint('views', __name__)

app = Flask(__name__)


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




@login_required
@views.route('/home', methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        unregister(request.form.get('reg').split('/'))
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

    return render_template("index.html", user = current_user, registered = registered, announcement2 = announcement2, pastevents = pastevent2, now = datetime.datetime.now())

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
                                    student = db.session.query(student_info).filter(student_info.student_id == current_user.student_id).first()
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
            unregister(register_id)            
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
             announcement_file = request.files['announcementFile']
             announcement_date = datetime.datetime.now()
             if len(announcement_title) < 1:
                 flash('Announcement title must be greater than 1 character.', category='error')
             elif len(announcement) < 1:
                 flash('Announcement must be greater than 1 character.', category='error')
             elif not allowed_file(announcement_file.filename):
                 flash('File extension is not allowed, only JPG, JPEG, PNG, PDF, DOC, DOCX, TXT, and GIF are allowed.', category='error')
             else:
                  announcement_file.save(os.path.join(basedir, app.config["UPLOAD_FOLDER"], announcement_file.filename))
                  filename = announcement_file.filename
                  new_announcement = announcements(announcement_date_time = announcement_date, announcement_title=announcement_title,  file_name = announcement_file.filename, announcement = announcement)
                  db.session.add(new_announcement)
                  db.session.commit()
                  
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
            event_file = request.files['event_file']
    
            if len(event_title) < 1:
                flash('Event title must be greater than 1 character.', category='error')
            elif len(event_location) < 1:
                flash('Location must be greater than 1 character.', category='error')
            elif not allowed_file(event_file.filename) and event_file.tell() != 0:
                flash('File extension is not allowed, only JPG, JPEG, PNG, PDF, DOC, DOCX, TXT, and GIF are allowed.', category='error')
            else:
                print(event_date)
                print(event_location)
                if (event_file.tell() == 0):
                    event_file.filename == None
                else:
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
                register_object.status = "Accepted"
                register_object.student.current_hours =  register_object.student.current_hours + register_object.event.event_hours
                register_object.student.pending_hours =  register_object.student.pending_hours - register_object.event.event_hours
                db.session.commit()
            elif decision_information[0] == "deny":
                register_object.status = "Denied"
                register_object.student.pending_hours =  register_object.student.pending_hours - register_object.event.event_hours
                db.session.commit()
 
        event = db.session.query(event_info).filter(event_info.event_id == id).first()
        print(event.event_name)
        return render_template("cannedfooddonation.html", event = event )




def unregister(register_id):
    status2 = db.session.query(registration).filter(registration.student_id == current_user.student_id, registration.event_id == register_id[1]).first()
    status2.status = "Unregistered"
    update_spots = db.session.query(event_info).filter(event_info.event_id == register_id[1]).first()
    update_spots.spots_available = update_spots.spots_available + 1
    current_user.pending_hours = current_user.pending_hours - update_spots.event_hours
    db.session.commit()


