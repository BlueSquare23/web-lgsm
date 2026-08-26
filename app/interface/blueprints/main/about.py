from flask_login import login_required, current_user
from flask import render_template

from app.interface.use_cases import get_template_config

from . import main_bp

######### About Page #########

@main_bp.route("/about", methods=["GET"])
@login_required
def about():
    config = get_template_config()
    return render_template(
        "about.html", user=current_user, _config=config
    )

