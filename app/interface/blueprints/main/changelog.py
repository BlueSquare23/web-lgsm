from flask_login import login_required, current_user
from flask import render_template

from app.interface.use_cases import read_changelog

from . import main_bp

######### Changelog Page #########

@main_bp.route("/changelog", methods=["GET"])
@login_required
def changelog():
    changelog_html = read_changelog()

    return render_template(
        "changelog.html", user=current_user, changelog_html=changelog_html
    )


