from flask_login import login_required, current_user
from flask import render_template, current_app

from app.utils import *
from app.models import GameServer
from app.services import ProcInfoService

from app.config.config_manager import ConfigManager
config = ConfigManager()

from . import main_bp

######### Home Page #########

@main_bp.route("/", methods=["GET"])
@main_bp.route("/home", methods=["GET"])
@login_required
def home():
# TODO: Most of the code for this route is logging. Maybe I need a dedicated
# route logger, where I can just say route, pass it current_app and it'll log
# everything I care about seeing for that route.

    current_app.logger.debug(log_wrap("config text_color", config.get('aesthetic','text_color')))

    current_app.logger.debug(log_wrap("current_user.username", current_user.username))
    current_app.logger.debug(log_wrap("current_user.role", current_user.role))
    current_app.logger.debug(
        log_wrap("current_user.permissions", current_user.permissions)
    )

    installed_servers = GameServer.query.all()
    for server in installed_servers:
        current_app.logger.info(server.id)

    current_app.logger.debug(log_wrap("installed_servers", installed_servers))
#    for proc_id, proc in ProcInfoService().get_all_processes().items():
#        current_app.logger.debug(log_wrap(proc_id, proc))

    return render_template(
        "home.html",
        user=current_user,
        all_game_servers=installed_servers,
        _config=config,
    )

