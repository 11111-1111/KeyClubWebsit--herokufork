from models import student_info, login_details
from flask import Blueprint, render_template, request, flash,  redirect, url_for 
from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import db
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message, Mail
from views import app
import time
from Config import Config
auth = Blueprint('auth', __name__)
app.config.from_object(Config)

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
    print("entered")
    admin = db.session.query(login_details).filter(login_details.id == '001').first()
    print(admin)
    if(admin is None):
        print("made it")
        app.config.from_object(Config)
        adminlog = login_details(id = '001', password = app.config['ADMIN_PASSWORD'])
        db.session.add(adminlog)
        db.session.commit()
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.enter'))

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
            new_login = login_details(id = studentID, password = generate_password_hash(password2, method = 'sha256').decode("utf-8", "ignore"))
            db.session.add(new_login)
            db.session.commit()
            flash('Account Created', category = 'sucess')
            new_user = student_info(student_id = studentID, email = email, first_name = firstName, last_name = lastName, 
            current_hours = 0, pending_hours = 0, boardMember = False, inductedMember = False, announcementnotifications = False, 
            approvalnotifications = False, eventnotifcations = False )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_login, remember = True)
            return redirect(url_for('views.home'))




    return  render_template("register.html")


def send_reset_email(user):
    print(user.student_id)
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='raymondmoy11@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:

    {url_for('auth.reset', token=token, _external=True)}

    If you did not make this request, then simply ignore this email and no change will be made.
    '''
    

    mail = Mail(app)
    mail.init_app(app)
    mail.send(msg)

@auth.route('/forgot', methods = ['GET', 'POST'])
def forgot():
    if current_user.is_authenticated:
        return render_template('reset password.html')
    if request.method == 'POST':
        student_id1 = int(request.form.get('student_id'))
        email = request.form.get('email')
        stu_id_query = db.session.query(student_info).filter(student_info.student_id == student_id1).first()
        email_query = db.session.query(student_info).filter(student_info.email == email).first()
        if str(stu_id_query) == str(email_query):
            user = stu_id_query
            print(str(stu_id_query))
            if stu_id_query == None:
               print("None")
            send_reset_email(user)
            flash('If an account matches these credentials, an email with password reset instructions will be sent to you.') 
            return redirect(url_for('auth.login'))
        else: 
            user = None
            flash(' If an account matches these credentials, an email with password reset instructions will not not be sent to you.')


    return render_template("forgot password page.html")

@auth.route('/forgot/<token>', methods = ['GET', 'POST'])
def reset(token):
    if current_user.is_authenticated:
        return render_template('reset password.html')
    user = student_info.verify_reset_token(token)
    if user is None:
        flash('That is an expired or invalid token', category='error')
        return redirect(url_for('forgot'))

    if request.method == 'POST':
        new_pswd = request.form.get('newpass')
        password_entry = request.form.get('pass')
        if password_entry == None:
            flash("Password cannot be blank.", category='error')
        elif len(password_entry) < 4: 
            flash("Password cannot be less than 4 characters.", category='error')
        elif new_pswd != password_entry:
            flash("Passwords must match.", category='error')
        else:
            new_password = generate_password_hash(password_entry, method = 'sha256')
            stu_id = user.student_id
            changed_user = db.session.query(login_details).filter(login_details.id == stu_id).first()
            changed_user.password = new_password
            db.session.commit()
            flash('Your password has been changed! You are now able to login.', category='success')
            time.sleep(3)
            return redirect(url_for('auth.login'))

    return render_template('reset password.html')
