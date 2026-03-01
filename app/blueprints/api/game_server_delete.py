import json

from flask import Response
from flask_login import login_required, current_user
from flask_restful import Resource

from app import db
from app.utils import *
#from app.models import GameServer
from app.services import ProcInfoRegistry
from app.config.config_manager import ConfigManager

config = ConfigManager()

from . import api

from app.container import container

######### API GameServer Delete #########

class GameServerDelete(Resource):
    @login_required
    def delete(self, server_id):
        global config
#        server = GameServer.query.filter_by(id=server_id).first()
        server = container.get_game_server().execute(server_id)
        if server == None:
            resp_dict = {"Error": "Server not found!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=404, mimetype="application/json"
            )
            return response

        server_name = server.install_name

        # NOTE: For everyone's safety, if config options are incongruous, default
        # to safer keep user, keep files option. (ie. If delete_user is True and
        # remove_files is False, default to keep user.
        if config.getboolean('settings', 'delete_user') and not config.getboolean('settings', 'remove_files'):
            config.set('settings', 'delete_user', False)

        # Check if user has permissions to delete route & server.
        if not container.check_user_access().execute(current_user.id, "delete", server_id):
            resp_dict = {
                "Error": f"Insufficient permission to delete {server.install_name}"
            }
            response = Response(
                json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
            )
            return response

        current_app.logger.info(log_wrap(f"{current_user} deleting ID: ", server_id))
        current_app.logger.info(server)

        # Delete cronjobs for server from DB.
        jobs_list = container.list_cron_jobs().execute(server.id)

        current_app.logger.info(log_wrap("job_list", jobs_list))

        if len(jobs_list) > 0:
            for job in jobs_list:
                container.delete_cron_job().execute(job.id)  ## TODO: Maybe we ought to consider doing a delete batch with context handler so we can bop over a forloop and only commit transaction at end. But for now this is fine. Long line is long...
                # Remove job from DB.

        # Drop any saved proc_info objects.
        ProcInfoRegistry().remove_process(server_id)

        # Log to ensure process was dropped.
        current_app.logger.info(log_wrap("All processes", ProcInfoRegistry().get_all_processes()))

        # TODO: Refactor this now that config handling has been changed.
#        if not delete_server(server, config.getboolean('settings','remove_files'), config.getboolean('settings','delete_user')):

        if not container.delete_game_server().execute(server.id, config.getboolean('settings','remove_files'), config.getboolean('settings','delete_user')):
            resp_dict = {
                "Error": "Problem deleting server, see error logs for more details."
            }
            response = Response(
                json.dumps(resp_dict, indent=4), status=500, mimetype="application/json"
            )
            return response

        delete_user = str(config.getboolean('settings','delete_user'))
        remove_files = str(config.getboolean('settings','remove_files'))
        container.log_audit_event().execute(current_user.id,  f"User '{current_user.username}', deleted game server '{server_name}', delete_user: {delete_user}, remove_file:{remove_files}")

        return "", 204

api.add_resource(GameServerDelete, "/delete/<string:server_id>")

