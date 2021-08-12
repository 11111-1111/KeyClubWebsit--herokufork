from sqlalchemy.orm import session
from sqlalchemy.sql.roles import OrderByRole
from website.models import announcements, event_info, registration, student_info
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
import datetime
from . import db
from sqlalchemy import asc, desc


views = Blueprint('views', __name__)

@login_required
@views.route('/home')
def home():
    registered = db.session.query(registration).join(event_info).filter(registration.student_id == current_user.student_id)
    registered = registered.filter(event_info.event_time >= datetime.datetime.now()) 
    registered = registered.order_by(event_info.event_time.asc()) 
    announcement2 = db.session.query(announcements).order_by(announcements.announcement_date_time)
    return render_template("index.html", user = current_user, announcement2 = announcement2)

@login_required
@views.route('/profile')
def profile(): 
     return render_template("profile.html")

@login_required
@views.route('/signup', methods = ['GET','POST']) 
def signup():
    if request.method == "POST":
        register_id = request.form.get("register_button")
        new_registeration = registration(
                            status = "Registered" , 
                            comments = None, time_submitted = datetime.datetime.now(), 
                            event = db.session.query(event_info).filter(event_info.event_id == register_id).first(),
                            student = db.session.query(student_info).filter(student_info.student_id == current_user.student_id).first()
                            )

        db.session.add(new_registeration)
        db.session.commit()

        update_spots = db.session.query(event_info).filter(event_info.event_id == register_id).first()
        update_spots.spots_available = update_spots.spots_available - 1
        db.session.commit()

        current_user.pending_hours = current_user.pending_hours + update_spots.event_hours
        db.session.commit()
        return redirect(url_for("views.home"))
        
    events1 = db.session.query(event_info).filter(event_info.event_time >= datetime.datetime.now())
    events1 = events1.order_by(event_info.event_time.asc()) 
    return render_template("signup.html", events = events1)

@login_required
@views.route('/createannouncement', methods = ['GET', 'POST'])
def createannouncement():
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
             else:
                  new_announcement = announcements(announcement_date_time = announcement_date, announcement_title=announcement_title, announcement=announcement, announcement_file=announcement_file.read())
                  db.session.add(new_announcement)
                  db.session.commit()
                  flash('Announcement sent successfully!', category='success')
        return render_template("createannouncement.html")

    else:
        flash("You cannot view this page", category = "error")
        return redirect(url_for("views.home"))  


@login_required
@views.route('/createevent', methods = ['GET', 'POST'])
def createevent():
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

            print(event_date)
            print(event_location)

            new_event = event_info(event_name = event_title, event_time = event_date, event_hours = event_hours, event_location = event_location,
            more_info = more_info, event_type = event_type, event_reccurent = False, spots_available = spots_available )

            db.session.add(new_event)
            db.session.commit()

            print(new_event.event_id)

            return redirect(url_for("views.signup"))



        return render_template("createevent.html")
    else:
        flash("You cannot view this page", category = "error")
        return redirect(url_for("views.home"))

@login_required
@views.route('/review')
def review():
    if(current_user.boardMember):
        return render_template("review.html")
    else:
        flash("You cannot view this page", category = "error")
        return redirect(url_for("views.home"))

