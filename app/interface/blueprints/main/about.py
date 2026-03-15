from flask_login import login_required, current_user
from flask import render_template

from app.container import container
from . import main_bp

######### About Page #########

@main_bp.route("/about", methods=["GET"])
@login_required
def about():
    config = container.get_template_config().execute()
    return render_template(
        "about.html", user=current_user, _config=config
    )

