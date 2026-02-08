from flask_login import login_required, current_user
from flask import render_template

# Needs config for text_color.
from app.config.config_manager import ConfigManager
config = ConfigManager()

from . import main_bp

######### About Page #########

@main_bp.route("/about", methods=["GET"])
@login_required
def about():
    global config
    return render_template(
        "about.html", user=current_user, _config=config
    )

