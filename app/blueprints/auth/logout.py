from flask_login import logout_user, login_required, current_user
from flask import redirect, url_for, flash

from app.utils import audit_log_event

from . import auth_bp


######### Logout Route #########

@auth_bp.route("/logout")
@login_required
def logout():
    audit_log_event(current_user.id, f"User '{current_user.username}' logged out")
    logout_user()
    flash("Logged out!", category="success")
    return redirect(url_for("auth.login"))

