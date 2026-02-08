from datetime import timedelta

from werkzeug.security import check_password_hash
from flask_login import (
    login_user,
    confirm_login,
    logout_user,
    current_user,
)
from flask import (
    render_template,
    redirect,
    url_for,
    request,
    flash,
    current_app,
)

from app.forms.auth import LoginForm 
from app.models import User
from app.utils import validation_errors, audit_log_event
from app.services import Blocklist

from . import auth_bp

######### Login Route #########

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Create LoginForm.
    form = LoginForm()

    if User.query.first() == None:
        flash("Please add a user!", category="success")
        return redirect(url_for("auth.setup"))

    blocklist = Blocklist()

    ip = blocklist.get_client_ip(request)

    if blocklist.is_blocked(ip):
        return 'Access denied', 403

    if request.method == "GET":
        return render_template("login.html", user=current_user, form=form), 200

    # Handle Invalid form submissions.
    if not form.validate_on_submit():
        validation_errors(form)
        return redirect(url_for("auth.login"))

    username = form.username.data
    password = form.password.data
    otp_code = form.otp_code.data

    # Check login info.
    user = User.query.filter_by(username=username).first()
    if user == None:
        blocklist.add_failed(ip)
        flash("Incorrect Username or Password!", category="error")
        return render_template("login.html", user=current_user, form=form), 403

    current_app.logger.info(user)

    if not check_password_hash(user.password, password):
        blocklist.add_failed(ip)
        flash("Incorrect Username or Password!", category="error")
        return render_template("login.html", user=current_user, form=form), 403

    if current_user.is_authenticated:
        logout_user()

    four_weeks_delta = timedelta(days=28)

    # Handle 2fa Logins.
    if user.otp_enabled:
        # For case where user is setting up otp for first time.
        if not user.otp_setup:
            login_user(user, remember=True, duration=four_weeks_delta)
            confirm_login()
            audit_log_event(user.id, f"User '{username}' logged in")
            flash("Please setup two factor authentication!", category="success")
            return redirect(url_for("auth.two_factor_setup"))

        if not user.verify_totp(otp_code):
            blocklist.add_failed(ip)
            flash("Invalid otp 2fa code!", category="error")
            return render_template("login.html", user=current_user, form=form), 403

    flash("Logged in!", category="success")
    login_user(user, remember=True, duration=four_weeks_delta)
    confirm_login()
    audit_log_event(user.id, f"User '{username}' logged in")
    return redirect(url_for("main.home"))


