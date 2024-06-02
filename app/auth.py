import os
import string
from . import db
from pathlib import Path
from .models import User
from .utils import contains_bad_chars
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask import Blueprint, render_template, redirect, url_for, request, \
                                                              flash, abort

auth = Blueprint("auth", __name__)

######### Login Route #########

@auth.route("/login", methods=['GET', 'POST'])
def login():
    # Set default return code.
    response_code = 200

    if User.query.first() == None:
        flash("Please add a user!", category='success')
        return redirect(url_for('auth.setup'))

    # Post route code for login form submission.
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        # Make sure required form items are supplied.
        for form_item in (username, password):
            if form_item == None or form_item == "":
                flash("Missing required form field(s)!", category='error')
                return redirect(url_for('auth.login'))

            # Check input lengths.
            if len(form_item) > 150:
                flash("Form field too long!", category='error')
                return redirect(url_for('auth.login'))

        # Check login info.
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect Username or Password!', category='error')
                response_code =  403
        else:
            flash('Incorrect Username or Password!', category='error')
            response_code =  403

    return render_template("login.html", user=current_user), response_code

######### Setup Route #########

@auth.route("/setup", methods=['GET', 'POST'])
def setup():
    # Set default response code.
    response_code = 200

    if request.method == 'POST':
        # Collect form data
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        # Make sure required form items are supplied.
        for form_item in (username, password1, password2):
            if form_item == None or form_item == "":
                flash("Missing required form field(s)!", category='error')
                return redirect(url_for('auth.setup'))

            # Check input lengths.
            if len(form_item) > 150:
                flash("Form field too long!", category='error')
                return redirect(url_for('auth.setup'))

        # Check if a user already exists and if so don't allow another user to
        # be created. Right now this is a single user interface. Could possible
        # expand it to mulitiple users in the future.
        if User.query.first() != None:
            flash("User already added. Please sign in!", category='error')
            return redirect(url_for('auth.login'))


        # Setup rudimentary password strength counter.
        lower_alpha_count = 0
        upper_alpha_count = 0
        number_count = 0
        special_char_count = 0

        # Adjust password strength values.
        for char in list(password1):
            if char in string.ascii_lowercase:
                lower_alpha_count += 1
            elif char in string.ascii_uppercase:
                upper_alpha_count += 1
            elif char in string.digits:
                number_count += 1
            else:
                special_char_count += 1

        ## Check if submitted form data for issues.
        # Verify password passes basic strength tests.
        if upper_alpha_count < 1 and number_count < 1 and special_char_count < 1:
            flash("Passwords doesn't meet criteria!", category='error')
            flash("Must contain: an upper case character, a number, and a \
                                    special character", category='error')
            response_code = 400

        # To try to nip xss & template injection in the bud.
        elif contains_bad_chars(username):
            flash("Username Contains Illegal Character(s)", category="error")
            flash(r"""Bad Chars: $ ' " \ # = [ ] ! < > | ; { } ( ) * , ? ~ &""", \
                                                        category="error")
            response_code = 400

        elif password1 != password2:
            flash('Passwords don\'t match!', category='error')
            response_code = 400

        elif len(password1) < 12:
            flash('Password is too short!', category='error')
            response_code = 400

        else:
            # Add the new_user to the database, then redirect home.
            new_user = User(username=username, \
                    password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()

            flash('User created!')
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))

    # If already a user added, disable the setup route.
    if User.query.first() == None:
        return render_template("setup.html", user=current_user), response_code
    else:
        flash("User already added. Please sign in!", category='error')
        return redirect(url_for('auth.login'))

######### Logout Route #########

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logged out!', category='success')
    return redirect(url_for("auth.login"))

