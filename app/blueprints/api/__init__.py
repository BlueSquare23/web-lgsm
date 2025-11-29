from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint("api", __name__)
api = Api(api_bp)

from . import cmd_output, game_server_delete, manage_cron, server_status, system_usage, update_console

