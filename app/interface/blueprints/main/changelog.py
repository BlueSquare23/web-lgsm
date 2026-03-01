import markdown

from flask_login import login_required, current_user
from flask import render_template

from app.utils import read_changelog

from . import main_bp

######### Changelog Page #########

@main_bp.route("/changelog", methods=["GET"])
@login_required
def changelog():
    changelog_md = read_changelog()
    changelog_html = markdown.markdown(changelog_md)

    return render_template(
        "changelog.html", user=current_user, changelog_html=changelog_html
    )


