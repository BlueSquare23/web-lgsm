import json

from flask import Response, flash
from flask_login import login_required, current_user
from flask_restful import Resource

from app import db
from app.utils import *

from . import api

from app.interface.use_cases import get_game_server, getboolean_config, set_config, check_user_access, list_cron_jobs, delete_cron_job, remove_process, list_processes, delete_game_server, log_audit_event

######### API GameServer Delete #########

class GameServerDelete(Resource):
    @login_required
    def delete(self, server_id):
        server = get_game_server(server_id)
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
        if getboolean_config('settings', 'delete_user') and not getboolean_config('settings', 'remove_files'):
            set_config('settings', 'delete_user', False)

        # Check if user has permissions to delete route & server.
        if not check_user_access(current_user.id, "delete", server_id):
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
        jobs_list = list_cron_jobs(server.id)

        current_app.logger.info(log_wrap("job_list", jobs_list))

        if len(jobs_list) > 0:
            for job in jobs_list:
                delete_cron_job(job.job_id)  ## TODO: Maybe we ought to consider doing a delete batch with context handler so we can bop over a forloop and only commit transaction at end. But for now this is fine. Long line is long...

        # Drop any saved proc_info objects.
        remove_process(server_id)

        # Log to ensure process was dropped.
        current_app.logger.info(log_wrap("All processes", list_processes()))

        remove_files = getboolean_config('settings','remove_files')
        delete_user = getboolean_config('settings','delete_user')

        errors = []

        if not delete_game_server(server.id, remove_files, delete_user, errors):
            resp_dict = {
                "Errors": errors
            }
            response = Response(
                json.dumps(resp_dict, indent=4), status=500, mimetype="application/json"
            )
            return response

        log_audit_event(current_user.id,  f"User '{current_user.username}', deleted game server '{server_name}', delete_user: {delete_user}, remove_file:{remove_files}")

        flash(f"Game server, {server.install_name} deleted!")  # I hate this but it works, so fine for now. TODO: FIX THIS!

        return "", 204

api.add_resource(GameServerDelete, "/delete/<string:server_id>")

