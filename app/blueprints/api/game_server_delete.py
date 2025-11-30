import json

from flask import Response
from flask_login import login_required, current_user
from flask_restful import Resource

from app import db
from app.utils import *
from app.models import GameServer, Job
from app.services import CronService, ProcInfoService
from app.config.config_manager import ConfigManager

config = ConfigManager()

from . import api

######### API GameServer Delete #########

class GameServerDelete(Resource):
    @login_required
    def delete(self, server_id):
        global config
        server = GameServer.query.filter_by(id=server_id).first()
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
        if not current_user.has_access("delete", server_id):
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
        cron = CronService(server.id)
        jobs_list = cron.list_jobs()

        current_app.logger.info(log_wrap("job_list", jobs_list))

        if len(jobs_list) > 0:
            for job in jobs_list:
                cronjob = Job.query.filter_by(id=job["job_id"]).first()
                # Remove job from DB.
                db.session.delete(cronjob)
            db.session.commit()

        # Drop any saved proc_info objects.
        ProcInfoService().remove_process(server_id)

        # Log to ensure process was dropped.
        current_app.logger.info(log_wrap("All processes", ProcInfoService().get_all_processes()))

        # TODO: Refactor this now that config handling has been changed.
        if not delete_server(server, config.getboolean('settings','remove_files'), config.getboolean('settings','delete_user')):
            resp_dict = {
                "Error": "Problem deleting server, see error logs for more details."
            }
            response = Response(
                json.dumps(resp_dict, indent=4), status=500, mimetype="application/json"
            )
            return response

        # We don't want to keep deleted servers in the cache.
        update_tmux_socket_name_cache(server_id, None, True)
        delete_user = str(config.getboolean('settings','delete_user'))
        remove_files = str(config.getboolean('settings','remove_files'))
        audit_log_event(current_user.id, f"User '{current_user.username}', deleted game server '{server_name}', delete_user: {delete_user}, remove_file:{remove_files}")

        return "", 204

api.add_resource(GameServerDelete, "/delete/<string:server_id>")

