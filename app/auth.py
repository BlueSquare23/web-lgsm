import os
from . import db
from pathlib import Path
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    status_code = 200
    if User.query.first() == None:
        flash("Please add a user!", category='success')
        return redirect(url_for('auth.setup'))

    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        # Check login info
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect Username or Password!', category='error')
                status_code =  403
        else:
            flash('Incorrect Username or Password!', category='error')
            status_code =  403

    return render_template("login.html", user=current_user), status_code

@auth.route("/setup", methods=['GET', 'POST'])
def setup():

    if request.method == 'POST':
        # Collect form data
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        # Check if submitted form data for issues 
        username_exists = User.query.filter_by(username=username).first()

        if username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match!', category='error')
        elif len(password1) < 8:
            flash('Password is too short.', category='error')
        else:
            # Add the new_user to the database, then redirect home.
            new_user = User(username=username, password=generate_password_hash(password1, method='sha256')) 
            db.session.add(new_user)
            db.session.commit()

            flash('User created!')
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))

    # If already a user added, disable the setup route.
    if User.query.first() == None:
        return render_template("setup.html", user=current_user)
    else:
        flash("User already added. Please sign in!", category='success')
        return redirect(url_for('auth.login'))

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logged out!', category='success')
    return redirect(url_for("views.home"))
