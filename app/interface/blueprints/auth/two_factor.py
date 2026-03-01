import os
import base64
import pyqrcode
from io import BytesIO

from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, request, flash

from app.interface.forms.auth import OTPSetupForm
from app.utils import validation_errors
from app.container import container

from . import auth_bp

# TODO: Add audit logging to this for when a user enables/disabled and
# successfully sets up two factor.

######### 2fa Setup Route #########

@auth_bp.route("/2fa_setup", methods=["GET", "POST"])
@login_required
def two_factor_setup():

    user = container.to_user().execute(current_user)
    form = OTPSetupForm()
    form.user_id = current_user.id

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
    user.otp_enabled = True
    container.edit_user().execute(**user.__dict__)
    return redirect(url_for("main.home"))


######### 2fa QRCode Route #########

@auth_bp.route('/qrcode')
@login_required
def qrcode():
    # Render qrcode, no caching.
    url = pyqrcode.create(container.get_user_totp_uri().execute(current_user.id))
    stream = BytesIO()
    url.svg(stream, scale=3)
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
