from flask_login import login_required, current_user
from flask import render_template, current_app

from app.utils import log_wrap

from . import main_bp

from app.interface.use_cases import list_user_game_servers, get_template_config

######### Home Page #########

@main_bp.route("/", methods=["GET"])
@main_bp.route("/home", methods=["GET"])
@login_required
def home():
# TODO: Most of the code for this route is logging. Maybe I need a dedicated
# route logger, where I can just say route, pass it current_app and it'll log
# everything I care about seeing for that route.

    config = get_template_config()
    current_app.logger.debug(log_wrap("config text_color", config.get('aesthetic','text_color')))

    current_app.logger.debug(log_wrap("current_user.username", current_user.username))
    current_app.logger.debug(log_wrap("current_user.role", current_user.role))
    current_app.logger.debug(
        log_wrap("current_user.permissions", current_user.permissions)
    )

    servers = list_user_game_servers(current_user.id)

    for server in servers:
        current_app.logger.info(server.id)

    current_app.logger.debug(log_wrap("servers", servers))

    return render_template(
        "home.html",
        user=current_user,
        servers=servers,
        _config=config,
    )


