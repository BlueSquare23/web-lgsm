import json
from datetime import timedelta

from werkzeug.security import generate_password_hash
from flask_login import (
    login_user,
    current_user,
)
from flask import (
    render_template,
    redirect,
    url_for,
    request,
    flash,
)

from app.interface.forms.auth import SetupForm
from app.interface.forms.validation_errors import validation_errors
from app.container import container

from app.interface.auth.auth_user import AuthUser

from . import auth_bp

######### Setup Route #########

@auth_bp.route("/setup", methods=["GET", "POST"])
def setup():
    # If already a user added, disable the setup route.
    if container.list_users().execute():
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
    enable_otp = form.enable_otp.data

    # Add the new_user to the database, then redirect home.
    new_user = {
        'id': None,
        'username': username,
        'password': generate_password_hash(password, method="pbkdf2:sha256"),
        'role': "admin",
        'permissions': json.dumps({"admin": True}),
        'otp_enabled': enable_otp,
        'otp_secret': None,
        'otp_setup': False,
    }
    user_id = container.edit_user().execute(**new_user)
    if not user_id:
        flash("Problem creating new user...", category="error")
        return redirect(url_for("auth.setup"))

    flash("User created!")

    four_weeks_delta = timedelta(days=28)
    auth_user = AuthUser(user_id)
    login_user(auth_user, remember=True, duration=four_weeks_delta)
    container.log_audit_event().execute(new_user["id"],  f"New user '{username}' created")

    if enable_otp:
        return redirect(url_for("auth.two_factor_setup"))

    return redirect(url_for("main.home"))


