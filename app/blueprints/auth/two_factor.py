import os
import base64
import pyqrcode
from io import BytesIO

from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, request, flash

from app import db
from app.forms.auth import OTPSetupForm
from app.models import User
from app.utils import validation_errors

from . import auth_bp

# TODO: Add audit logging to this for when a user enables/disabled and
# successfully sets up two factor.

######### 2fa Setup Route #########

@auth_bp.route("/2fa_setup", methods=["GET", "POST"])
@login_required
def two_factor_setup():
    user = User.query.filter_by(username=current_user.username).first()
    if user is None:
        return redirect(url_for("logout"))

    # Setup otp_secret if doesn't already exist (for legacy user compat).
    if user.otp_secret is None:
        user.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')
        db.session.commit()

    form = OTPSetupForm()
    form.user_id = user.id

    if request.method == "GET":
        # Format the secret for easier manual entry (add spaces every 4 characters).
        formatted_secret = ' '.join([user.otp_secret[i:i+4] for i in range(0, len(user.otp_secret), 4)])

        # Don't cache qrcode!
        return render_template('2fa_setup.html', user=current_user, form=form, fsecret=formatted_secret), 200, {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }

    # Handle Invalid form submissions.
    if not form.validate_on_submit():
        validation_errors(form)
        return redirect(url_for("auth.two_factor_setup"))
    
    flash("Two factor enabled successfully!", category="success")
    user.otp_setup = True
    db.session.commit()
    return redirect(url_for("main.home"))


######### 2fa QRCode Route #########

@auth_bp.route('/qrcode')
@login_required
def qrcode():
    user = User.query.filter_by(username=current_user.username).first()
    if user is None:
        return redirect(url_for("logout"))

    # Render qrcode, no caching.
    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=3)
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
