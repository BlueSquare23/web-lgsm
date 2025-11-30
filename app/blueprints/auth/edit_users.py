import json

from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
from flask import (
    render_template,
    redirect,
    url_for,
    request,
    flash,
    current_app,
)

from app import db
from app.forms.auth import EditUsersForm
from app.models import User, GameServer
from app.utils import validation_errors, log_wrap, audit_log_event

from . import auth_bp

######### Create / Edit User(s) Route #########

@auth_bp.route("/edit_users", methods=["GET", "POST"])
@login_required
def edit_users():
    if current_user.role != "admin":
        flash("Only Admins are allowed to edit users!", category="error")
        return redirect(url_for("main.home"))

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

    # TODO: Tweak this GET logic and Jinja2 template code. Make it pass
    # user_ident object to template instead of passing derivatives of that
    # object.

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
            user_otp_enabled = None
        else:
            user_role = user_ident.role
            user_permissions = user_ident.permissions
            user_otp_enabled = user_ident.otp_enabled

        return render_template(
            "edit_users.html",
            user=current_user,
            installed_servers=installed_servers,
            controls=all_controls,
            all_users=all_users,
            selected_user=selected_user,
            user_role=user_role,
            user_otp_enabled=user_otp_enabled,
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
    enable_otp = form.enable_otp.data
    is_admin = form.is_admin.data
    install = form.install.data
    add = form.add.data
    settings = form.settings.data
    edit = form.edit.data
    jobs = form.jobs.data
    delete = form.delete.data
    controls = form.controls.data
    server_ids = form.server_ids.data

    # Debug logging for post args.
    current_app.logger.debug(log_wrap("selected_user", selected_user))
    current_app.logger.debug(log_wrap("change_user_pass", change_user_pass))
    current_app.logger.debug(log_wrap("username", username))
    current_app.logger.debug(log_wrap("password1", password1))
    current_app.logger.debug(log_wrap("password2", password2))
    current_app.logger.debug(log_wrap("enable_otp", enable_otp))
    current_app.logger.debug(log_wrap("is_admin", is_admin))
    current_app.logger.debug(log_wrap("install", install))
    current_app.logger.debug(log_wrap("add", add))
    current_app.logger.debug(log_wrap("settings", settings))
    current_app.logger.debug(log_wrap("edit", edit))
    current_app.logger.debug(log_wrap("jobs", jobs))
    current_app.logger.debug(log_wrap("delete", delete))
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

    # Page access controls
    permissions["install"] = False
    if install:
        permissions["install"] = True

    permissions["add"] = False
    if add:
        permissions["add"] = True

    permissions["settings"] = False
    if settings:
        permissions["settings"] = True

    permissions["edit"] = False
    if edit:
        permissions["edit"] = True

    permissions["jobs"] = False
    if jobs:
        permissions["jobs"] = True

    permissions["delete"] = False
    if delete:
        permissions["delete"] = True

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
            otp_enabled=enable_otp,
        )

        # Reset otp setup
        if not enable_otp:
            new_user.otp_setup = False

        db.session.add(new_user)
        db.session.commit()
        audit_log_event(current_user.id, f"User '{current_user.username}', created new user '{username}'")
        flash("New User Added!")
        return redirect(url_for("main.home"))

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

    # Reset otp setup
    if not enable_otp:
        user_ident.otp_setup = False

    user_ident.role = role
    user_ident.otp_enabled = enable_otp
    user_ident.permissions = json.dumps(permissions)
    db.session.commit()
    audit_log_event(current_user.id, f"User '{current_user.username}', changed permissions for user '{username}'")
    flash(f"User {username} Updated!")
    return redirect(url_for("auth.edit_users", username=username))

