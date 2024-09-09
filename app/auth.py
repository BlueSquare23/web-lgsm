import os
import json
from . import db
from pathlib import Path
from datetime import timedelta
from .models import User, GameServer
from .utils import check_require_auth_setup_fields, valid_password
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, confirm_login, logout_user, login_required, current_user
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort

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
# TODO; Turn these into debug prints.
#            print(user.username)
#            print(user.role)
#            print(user.permissions)
            if check_password_hash(user.password, password):
                if current_user.is_authenticated:
                    logout_user()
                flash("Logged in!", category='success')
                four_weeks_delta = timedelta(days=28)
                login_user(user, remember=True, duration=four_weeks_delta)
                confirm_login()
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
        if not check_require_auth_setup_fields(username, password1, password2):
            return redirect(url_for('auth.setup'))

        # Check if a user already exists and if so don't allow another user to
        # be created. Only allow authenticated admin users to create new users
        # after initial setup.
        if User.query.first() != None:
            flash("User already added. Please sign in!", category='error')
            return redirect(url_for('auth.login'))

        if not valid_password(password1, password2):
            return redirect(url_for('auth.setup'))

        # Add the new_user to the database, then redirect home.
        new_user = User(username=username, \
                password=generate_password_hash(password1, method='pbkdf2:sha256'), \
                role='admin', permissions=json.dumps({'admin': True}))
        db.session.add(new_user)
        db.session.commit()

        flash('User created!')
        login_user(new_user, remember=True)
        return redirect(url_for('views.home'))

    # If already a user added, disable the setup route.
    if User.query.first() != None:
        flash("User already added. Please sign in!", category='error')
        return redirect(url_for('auth.login'))

    return render_template("setup.html", user=current_user), response_code

######### Logout Route #########

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logged out!', category='success')
    return redirect(url_for("auth.login"))

######### Create / Edit User(s) Route #########

@auth.route("/edit_users", methods=['GET', 'POST'])
@login_required
def edit_users():
    if current_user.role != 'admin':
        flash("Only Admins are allowed to edit users!", category='error')
        return redirect(url_for('views.home'))

    installed_servers = GameServer.query.all()
    all_server_names = [server.install_name for server in installed_servers]
    all_controls = ["start", "stop", "restart", "monitor", "test-alert", "details",
                "postdetails", "update-lgsm", "update", "backup", "console", "send"]

    all_users = User.query.all()

    if request.method == 'GET':
        selected_user = request.args.get("username")
        delete = request.args.get("delete")

        user_ident = User.query.filter_by(username=selected_user).first()
        if user_ident == None and selected_user != 'newuser':
            return redirect(url_for('auth.edit_users', username='newuser'))

        if selected_user == 'newuser' and delete == 'true':
            flash("Can't delete user that doesn't exist yet!", category='error')
            return redirect(url_for('auth.edit_users'))

        if selected_user != 'newuser' and delete == 'true':
            if user_ident.username == current_user.username:
                flash("Cannot delete currently logged in user!", category='error')
                return redirect(url_for('auth.edit_users'))

            db.session.delete(user_ident)
            db.session.commit()
            flash(f"User {selected_user} deleted!")
            return redirect(url_for('auth.edit_users'))

        if user_ident == None:
            user_role = None
            user_permissions = None
        else:
            user_role = user_ident.role
            user_permissions = user_ident.permissions

        return render_template("edit_users.html", user=current_user, installed_servers=installed_servers, controls=all_controls, all_users=all_users, selected_user=selected_user, user_role=user_role, user_permissions=user_permissions)

    if request.method == 'POST':
        selected_user = request.form.get("selected_user")
        change_user_pass = request.form.get("change_username_password")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        is_admin = request.form.get("is_admin")
        install_servers = request.form.get("install_servers")
        add_servers = request.form.get("add_servers")
        mod_settings = request.form.get("mod_settings")
        edit_cfgs = request.form.get("edit_cfgs")
        delete_server = request.form.get("delete_server")
        controls = request.form.getlist("controls")
        servers = request.form.getlist("servers")

        if selected_user == 'newuser' or change_user_pass == 'true':
            if not check_require_auth_setup_fields(username, password1, password2):
                return redirect(url_for('auth.edit_users'))

            if not valid_password(password1, password2):
                return redirect(url_for('auth.edit_users'))

        user_ident = None
        if selected_user != 'newuser':
            user_ident = User.query.filter_by(username=username).first()
            if user_ident == None:
                flash("Invalid user selected!", category='error')
                return redirect(url_for('auth.edit_users'))


        permissions = dict()
        role = 'user' # Default to user role.

        permissions['install_servers'] = False
        if install_servers == 'true':
            permissions['install_servers'] = True

        permissions['add_servers'] = False
        if add_servers == 'true':
            permissions['add_servers'] = True

        permissions['mod_settings'] = False
        if mod_settings == 'true':
            permissions['mod_settings'] = True

        permissions['edit_cfgs'] = False
        if edit_cfgs == 'true':
            permissions['edit_cfgs'] = True

        permissions['delete_server'] = False
        if delete_server == 'true':
            permissions['delete_server'] = True

        permissions['controls'] = []
        if controls:
            # Validate supplied control(s) are in allowed list.
            for control in controls:
                if control not in all_controls:
                    flash("Invalid Control Supplied!", category='error')
                    return redirect(url_for('auth.edit_users'))
            permissions['controls'] = controls

        permissions['servers'] = []
        if servers:
            # Validate supplied server(s) are in installed list.
            for server in servers:
                if server not in all_server_names:
                    flash("Invalid Server Supplied!", category='error')
                    return redirect(url_for('auth.edit_users'))
            permissions['servers'] = servers 

        # Only explicitly set admin if supplied.
        if is_admin != None:
            if is_admin == 'true':
                role = 'admin'

        if selected_user == 'newuser':
            # Add the new_user to the database, then redirect home.
            new_user = User(username=username, \
                    password=generate_password_hash(password1, method='pbkdf2:sha256'), \
                    role=role, permissions=json.dumps(permissions))
            db.session.add(new_user)
            db.session.commit()
            flash("New User Added!")
            return redirect(url_for('views.home'))

        if change_user_pass == 'true':
            user_ident.username = username
            user_ident.password = generate_password_hash(password1, method='pbkdf2:sha256')
            user_ident.role = role
            user_ident.permissions = json.dumps(permissions)
            db.session.commit()
            flash(f"User {username} Updated!")
            return redirect(url_for('auth.edit_users', username=username))

        user_ident.role = role
        user_ident.permissions = json.dumps(permissions)
        db.session.commit()
        flash(f"User {username} Updated!")
        return redirect(url_for('auth.edit_users', username=username))

