from .models import student_info, login_details, announcements
from flask import Blueprint, render_template, request, flash,  redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

@auth.route('/logins', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        stu = request.form.get('stu')
        password = request.form.get('pass')
        user = login_details.query.filter_by(id = stu).first()
        if user: 
            if check_password_hash(user.password, password):
                flash('Logged in sucessfully!', category = 'sucess')
                login_user(user, remember = True)
                return redirect(url_for('views.home'))

            else:
                flash('Incorrect Password, try again', category = 'error')

        else: 
            flash("Account with that Student ID Does Not Exist", category = 'error')
        
    
    return render_template("logins.html")

@auth.route('/')
def enter():
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        conditionmet = True
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        studentID = request.form.get('studentID')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = login_details.query.filter_by(id = studentID).first()
        if user:
            flash('Account With That Student ID Already Exists', category = 'error')
        elif len(email) < 4:
            flash('Email must be greater than 4 charecters', category = 'error')
        elif len(firstName) < 2:
            flash('First Name must be greater than 2 charecters', category = 'error')
        elif password1 != password2:
            flash('Two passwords do not match', category = 'error')
        elif len(password1) < 4:
            flash('Password must be greater than 4 charecters', category = 'error')
        else: 
            new_login = login_details(id = studentID, password = generate_password_hash(password2, method = 'sha256'))
            db.session.add(new_login)
            db.session.commit()
            flash('Account Created', category = 'sucess')
            new_user = student_info(student_id = studentID, email = email, first_name = firstName, last_name = lastName, 
            current_hours = 0, pending_hours = 0, boardMember = True, inductedMember = False, 
            verifiedMember = False)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_login, remember = True)
            return redirect(url_for('views.home'))




    return  render_template("register.html")



@auth.route('/createannouncement', methods = ['GET', 'POST'])
def createAnnouncement():
    if request.method == 'POST':
        announcement_title = request.form.get('announcementTitle')
        announcement = request.form.get('summernote')
        announcement_file = request.files['announcementFile']

        if len(announcement_title) < 1:
            flash('Announcement title must be greater than 1 character.', category='error')
        elif len(announcement) < 1:
            flash('Announcement must be greater than 1 character.', category='error')
        else:
            new_announcement = announcements(announcement_title=announcement_title, announcement=announcement, announcement_file=announcement_file.read())
            db.session.add(new_announcement)
            db.session.commit()
            flash('Announcement sent successfully!', category='success')
    return render_template("createannouncement.html")
