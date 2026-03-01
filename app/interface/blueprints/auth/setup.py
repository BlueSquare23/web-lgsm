import json

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
from app.utils import validation_errors
from app.container import container

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
        'username': username,
        'password': generate_password_hash(password, method="pbkdf2:sha256"),
        'role': "admin",
        'permissions': json.dumps({"admin": True}),
        'otp_enabled': enable_otp,
    }
    container.update_user().execute(**new_user)

    flash("User created!")
    login_user(new_user, remember=True)
    container.log_audit_event().execute(new_user.id,  f"New user '{username}' created")

    if enable_otp:
        return redirect(url_for("auth.two_factor_setup"))

    return redirect(url_for("main.home"))


