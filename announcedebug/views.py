from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
views = Blueprint('views', __name__)

@login_required
@views.route('/home')
def home(): 
    return render_template("index.html", user = current_user)

@login_required
@views.route('/profile')
def profile(): 
     return render_template("profile.html")

@login_required
@views.route('/signup')
def signup():
     return render_template("signup.html")

@login_required
@views.route('/createannouncement')
def createannouncement():
    if(current_user.boardMember):
        return render_template("createannouncement.html")
    else:
        flash("You cannot view this page", category = "error")
        return redirect(url_for(request.url_rule.endpoint))

@login_required
@views.route('/createevent')
def createevent():
    if(current_user.boardMember):
        return render_template("createevent.html")
    else:
        flash("You cannot view this page", category = "error")
        return redirect(url_for("views.home"))



@login_required
@views.route('/createcannedfooddonation')
def createcannedfood():
    if(current_user.boardMember):
        return render_template("createcannedfood.html")
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

