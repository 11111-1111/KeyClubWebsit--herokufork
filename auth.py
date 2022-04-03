from email.message import EmailMessage
from models import student_info, login_details
from flask import Blueprint, render_template, request, flash,  redirect, url_for 
from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import db
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message, Mail
from views import app
import time
from Config import Config
import requests
import json
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, IntegerField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, InputRequired, Length, EqualTo
from flask_talisman import Talisman
talisman = Talisman(app, content_security_policy = None)

auth = Blueprint('auth', __name__)
app.config.from_object(Config)
#Create a form class and a csrf token:
class RegisterForm(FlaskForm):
    email = StringField("Please enter your email adress", validators=[DataRequired(), InputRequired(), Email(), Length(min = 5, max = 100, message = "Email must be between 5 and 100 charecters long")]) 
    firstName = StringField("Please enter your first name", validators = [DataRequired(), InputRequired(), Length(max = 20, message = "First name cannot be longer than 20 charecters" ) ])
    lastName = StringField("Please enter your last name", validators = [DataRequired(), InputRequired(), Length(max = 20, message = "Last name cannot be longer than 20 charecters ") ])
    studentID = StringField("Please enter your student id:", validators = [DataRequired(), InputRequired()])
    password1 = PasswordField("Please enter your password", validators = [DataRequired(), InputRequired(), Length(min = 4, message = "Password must be longer than 4 charecters")])
    password2 = PasswordField("Please retype your password", validators = [DataRequired(), InputRequired(), EqualTo('password1', message = "Passwords must match")])
    recaptcha = RecaptchaField() 
    submit = SubmitField("Submit")


 

@auth.route('/logins', methods = ['GET', 'POST'])
@talisman(force_https=True)
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
        adminlog = login_details(id = '001', password = generate_password_hash(app.config['ADMIN_PASSWORD'], method='sha256'))
        db.session.add(adminlog)
        db.session.commit()
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.enter'))

@auth.route('/register', methods = ['GET', 'POST'])
@talisman(force_https=True)
def register():
    registerForm = RegisterForm()
    email = None
    firstName = None
    lastName = None
    studentID = None
    password1 = None
    password2 = None
    if(registerForm.validate_on_submit() == False):
        try:
            flash(list(registerForm.errors.values())[0][0], category = 'error')
        except:
            pass
    else:
        email = registerForm.email.data
        registerForm.email.data = ''
        firstName = registerForm.firstName.data
        registerForm.firstName.data = ''
        lastName = registerForm.lastName.data
        registerForm.lastName.data = ''
        studentID = registerForm.studentID.data
        registerForm.studentID.data = ''
        password = registerForm.password1.data
        registerForm.password1.data = ''
        registerForm.password2.data = ''
        user = login_details.query.filter_by(id = studentID).first()
        user_email = student_info.query.filter_by(email = email).first()
        if user:
            flash('Account With That Student ID Already Exists', category = 'error')
        elif user_email:
            flash("Account With That Email Already Exists", category = 'error')
        else: 
            new_login = login_details(id = studentID, password = generate_password_hash(password, method = 'sha256'))
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




    return  render_template("register.html", form = registerForm)


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
