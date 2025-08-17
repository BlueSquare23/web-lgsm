import json
from . import db
from datetime import timedelta
from .models import User, GameServer
from .utils import validation_errors, log_wrap, audit_log_event
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    login_user,
    confirm_login,
    logout_user,
    login_required,
    current_user,
)
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    current_app,
)
from .forms import LoginForm, SetupForm, EditUsersForm

auth = Blueprint("auth", __name__)

######### Login Route #########

@auth.route("/login", methods=["GET", "POST"])
def login():
    # Create LoginForm.
    form = LoginForm()

    if User.query.first() == None:
        flash("Please add a user!", category="success")
        return redirect(url_for("auth.setup"))

    if request.method == "GET":
        return render_template("login.html", user=current_user, form=form), 200

    # Handle Invalid form submissions.
    if not form.validate_on_submit():
        validation_errors(form)
        return redirect(url_for("auth.login"))

    username = form.username.data
    password = form.password.data

    # Check login info.
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash("Incorrect Username or Password!", category="error")
        return render_template("login.html", user=current_user, form=form), 403

    current_app.logger.info(user)

    if not check_password_hash(user.password, password):
        flash("Incorrect Username or Password!", category="error")
        return render_template("login.html", user=current_user, form=form), 403

    if current_user.is_authenticated:
        logout_user()

    flash("Logged in!", category="success")
    four_weeks_delta = timedelta(days=28)
    login_user(user, remember=True, duration=four_weeks_delta)
    confirm_login()
    audit_log_event(user.id, f"User '{username}' logged in")
    return redirect(url_for("views.home"))


######### Setup Route #########

@auth.route("/setup", methods=["GET", "POST"])
def setup():
    # If already a user added, disable the setup route.
    if User.query.first() != None:
        flash("User already added. Please sign in!", category="error")
        return redirect(url_for("auth.login"))

    # Create SetupForm.
    form = SetupForm()

    if request.method == "GET":
        return render_template("setup.html", form=form, user=current_user), 200

    # Handle Invalid form submissions.
    if not form.validate_on_submit():
        validation_errors(form)
        return redirect(url_for("auth.login"))

    # Collect form data
    username = form.username.data
    password = form.password1.data

    # Add the new_user to the database, then redirect home.
    new_user = User(
        username=username,
        password=generate_password_hash(password, method="pbkdf2:sha256"),
        role="admin",
        permissions=json.dumps({"admin": True}),
    )
    db.session.add(new_user)
    db.session.commit()
    db.session.refresh(new_user)

    flash("User created!")
    login_user(new_user, remember=True)
    audit_log_event(new_user.id, f"New user '{username}' created")
    return redirect(url_for("views.home"))


######### Logout Route #########

@auth.route("/logout")
@login_required
def logout():
    audit_log_event(current_user.id, f"User '{current_user.username}' logged out")
    logout_user()
    flash("Logged out!", category="success")
    return redirect(url_for("auth.login"))


######### Create / Edit User(s) Route #########

@auth.route("/edit_users", methods=["GET", "POST"])
@login_required
def edit_users():
    if current_user.role != "admin":
        flash("Only Admins are allowed to edit users!", category="error")
        return redirect(url_for("views.home"))

    installed_servers = GameServer.query.all()
    all_server_ids = [server.id for server in installed_servers]
    all_controls = [
        "start",
        "stop",
        "restart",
        "monitor",
        "test-alert",
        "details",
        "postdetails",
        "update-lgsm",
        "update",
        "backup",
        "console",
        "send",
    ]

    all_users = User.query.all()
    form = EditUsersForm()

    # Dynamically set the choices for the SelectMultipleFields.
    form.controls.choices = [(control, control) for control in all_controls]
    form.server_ids.choices = [
        (server.id, server.install_name) for server in installed_servers
    ]

    if request.method == "GET":
        selected_user = request.args.get("username")
        # TODO (eventually): Make delete user work same way as delete server;
        # api route for delete user, button triggers js fetch req DELETE to API.
        delete = request.args.get("delete")

        user_ident = User.query.filter_by(username=selected_user).first()
        if user_ident == None and selected_user != "newuser":
            return redirect(url_for("auth.edit_users", username="newuser"))

        if selected_user == "newuser" and delete == "true":
            flash("Can't delete user that doesn't exist yet!", category="error")
            return redirect(url_for("auth.edit_users"))

        if selected_user != "newuser" and delete == "true":
            if user_ident.username == current_user.username:
                flash("Cannot delete currently logged in user!", category="error")
                return redirect(url_for("auth.edit_users"))

            if user_ident.id == 1:
                flash(
                    "Cannot delete main admin user! Anti-lockout protection!",
                    category="error",
                )
                return redirect(url_for("auth.edit_users"))

            db.session.delete(user_ident)
            db.session.commit()
            audit_log_event(current_user.id, f"User '{current_user.username}', deleted user '{selected_user}'")
            flash(f"User {selected_user} deleted!")
            return redirect(url_for("auth.edit_users"))

        if user_ident == None:
            user_role = None
            user_permissions = None
        else:
            user_role = user_ident.role
            user_permissions = user_ident.permissions

        return render_template(
            "edit_users.html",
            user=current_user,
            installed_servers=installed_servers,
            controls=all_controls,
            all_users=all_users,
            selected_user=selected_user,
            user_role=user_role,
            user_permissions=user_permissions,
            form=form,
        )

    # Handle POSTs.

    # TODO v1.9: Fix change username! Make user lookup work via ID instead of
    # username. That way we can accept a new username for a given ID and do
    # lookup with ID instead of username, then update that users info with
    # newly supplied instead.

    # Handle Invalid form submissions.
    if not form.validate_on_submit():
        validation_errors(form)
        return redirect(url_for("auth.edit_users"))

    selected_user = form.selected_user.data
    change_user_pass = form.change_username_password.data
    username = form.username.data
    password1 = form.password1.data
    password2 = form.password2.data
    is_admin = form.is_admin.data
    install_servers = form.install_servers.data
    add_servers = form.add_servers.data
    mod_settings = form.mod_settings.data
    edit_cfgs = form.edit_cfgs.data
    edit_jobs = form.edit_jobs.data
    delete_server = form.delete_server.data
    controls = form.controls.data
    server_ids = form.server_ids.data

    # Debug logging for post args.
    current_app.logger.debug(log_wrap("selected_user", selected_user))
    current_app.logger.debug(log_wrap("change_user_pass", change_user_pass))
    current_app.logger.debug(log_wrap("username", username))
    current_app.logger.debug(log_wrap("password1", password1))
    current_app.logger.debug(log_wrap("password2", password2))
    current_app.logger.debug(log_wrap("is_admin", is_admin))
    current_app.logger.debug(log_wrap("install_servers", install_servers))
    current_app.logger.debug(log_wrap("add_servers", add_servers))
    current_app.logger.debug(log_wrap("mod_settings", mod_settings))
    current_app.logger.debug(log_wrap("edit_cfgs", edit_cfgs))
    current_app.logger.debug(log_wrap("edit_jobs", edit_jobs))
    current_app.logger.debug(log_wrap("delete_server", delete_server))
    current_app.logger.debug(log_wrap("controls", controls))
    current_app.logger.debug(log_wrap("server_ids", server_ids))

    # TODO: Eventually this should probably be in FlaskForm validator.
    if selected_user == "newuser":
        for user in all_users:
            if user.username == username:
                flash(
                    "Cannot add new user with existing username!",
                    category="error",
                )
                return redirect(url_for("auth.edit_users"))

    user_ident = None
    if selected_user != "newuser":
        user_ident = User.query.filter_by(username=username).first()
        if user_ident == None:
            flash("Invalid user selected!", category="error")
            return redirect(url_for("auth.edit_users"))

        if user_ident.id == 1:
            flash(
                "Cannot modify main admin user's permissions! Anti-lockout protection!",
                category="error",
            )
            return redirect(url_for("auth.edit_users"))

    permissions = dict()
    role = "user"  # Default to user role.

    permissions["install_servers"] = False
    if install_servers:
        permissions["install_servers"] = True

    permissions["add_servers"] = False
    if add_servers:
        permissions["add_servers"] = True

    permissions["mod_settings"] = False
    if mod_settings:
        permissions["mod_settings"] = True

    permissions["edit_cfgs"] = False
    if edit_cfgs:
        permissions["edit_cfgs"] = True

    permissions["edit_jobs"] = False
    if edit_jobs:
        permissions["edit_jobs"] = True

    permissions["delete_server"] = False
    if delete_server:
        permissions["delete_server"] = True

    permissions["controls"] = []
    if controls:
        # Validate supplied control(s) are in allowed list.
        for control in controls:
            if control not in all_controls:
                flash("Invalid Control Supplied!", category="error")
                return redirect(url_for("auth.edit_users"))
        permissions["controls"] = controls

    permissions["server_ids"] = []
    if server_ids:
        # Validate supplied server_id(s) are in installed list.
        for server_id in server_ids:
            if server_id not in all_server_ids:
                flash("Invalid Server Supplied!", category="error")
                return redirect(url_for("auth.edit_users"))
        permissions["server_ids"] = server_ids

    # Only explicitly set admin if supplied.
    if is_admin == "true":
        role = "admin"

    if selected_user == "newuser":
        # Add the new_user to the database, then redirect home.
        new_user = User(
            username=username,
            password=generate_password_hash(password1, method="pbkdf2:sha256"),
            role=role,
            permissions=json.dumps(permissions),
        )
        db.session.add(new_user)
        db.session.commit()
        audit_log_event(current_user.id, f"User '{current_user.username}', created new user '{username}'")
        flash("New User Added!")
        return redirect(url_for("views.home"))

    # This is a bool because it comes from a toggle, whereas above inputs are
    # from radios, so are str "true/false". Confusing I know, sorry. Will get my
    # shit 2g3th3r 2m0rr0w.
    if change_user_pass:
        user_ident.username = username
        user_ident.password = generate_password_hash(password1, method="pbkdf2:sha256")
        user_ident.role = role
        user_ident.permissions = json.dumps(permissions)
        db.session.commit()
        audit_log_event(current_user.id, f"User '{current_user.username}', changed password for user '{username}'")
        flash(f"User {username} Updated!")
        return redirect(url_for("auth.edit_users", username=username))

    user_ident.role = role
    user_ident.permissions = json.dumps(permissions)
    db.session.commit()
    audit_log_event(current_user.id, f"User '{current_user.username}', changed permissions for user '{username}'")
    flash(f"User {username} Updated!")
    return redirect(url_for("auth.edit_users", username=username))

