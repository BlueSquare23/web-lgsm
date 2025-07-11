import json

from flask import Blueprint, Response, jsonify, request
from flask_login import login_required, current_user
from flask_restful import Api, Resource
from cron_converter import Cron

from .utils import *
from .models import *
from .cron import CronService
from .proc_info_vessel import ProcInfoVessel
from .processes_global import *

api_bp = Blueprint("api", __name__)
api = Api(api_bp)

######### API Cron Manager #########

class ManageCron(Resource):
    def check_perms(self):
        if not user_has_permissions(current_user, "jobs"):
            resp_dict = { "Error": f"Insufficient permission" }
            response = Response(
                json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
            )
            return (False, response)
        return (True, None)

    @login_required
    def get(self, server_id, job_id=None):
        allowed, resp = self.check_perms()
        if not allowed:
            return resp

        cron = CronService(server_id)
        jobs_list = cron.list_jobs()

        if job_id:
            for job in jobs_list:
                if job['server_id'] == server_id and job['job_id'] == job_id:
                    return jsonify(job)
            return ('Not found', 404)

        return jsonify(jobs_list)

    @login_required
    def post(self, server_id, job_id=None):
        allowed, resp = self.check_perms()
        if not allowed:
            return resp

        data = request.json
        cron = CronService(server_id)

        command = data.get('command')
        custom = data.get('custom')
        comment = data.get('comment')
        cron_expression = data.get('cron_expression')

        try:
            Cron(cron_expression)
        except ValueError:
            return {'Error':'Invalid cron expression'}, 400

        if command == 'send':
            command = f"send {custom}"

        if command == 'custom':
            command = f"custom: {custom}"

        job = {
            'expression': cron_expression,
            'command': command,
            'server_id': server_id,
            'job_id': job_id,
            'comment': comment,
        }

        if cron.edit_job(job):
            return {'success':'job updated'}, 201
        else:
            return {'error':'problem updating job'}, 500

    @login_required
    def delete(self, server_id, job_id):
        allowed, resp = self.check_perms()
        if not allowed:
            return resp

        cron = CronService(server_id)
        if cron.delete_job(job_id):
            audit_log_event(current_user.id, f"User '{current_user.username}', deleted job_id '{job_id}' for server_id '{server_id}'")
            return '', 204

        return 500

api.add_resource(
    ManageCron,
    "/cron/<string:server_id>",
    "/cron/<string:server_id>/<string:job_id>"
)

######### API Update Console #########

class UpdateConsole(Resource):
    @login_required
    def post(self, server_id):
        if not user_has_permissions(current_user, "update-console"):
            resp_dict = {"Error": "Permission denied!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
            )
            return response

        # Check that the submitted server exists in db.
        server = GameServer.query.filter_by(id=server_id).first()
        if server == None:
            resp_dict = {"Error": "Supplied server does not exist!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
            )
            return response

        tmux_socket = get_tmux_socket_name(server)

        cmd = [
            PATHS["tmux"],
            "-L",
            tmux_socket,
            "capture-pane",
            "-pt",
            server.script_name,
            "-S",
            "-",
            "-E",
            "-",
            "-J",
        ]

        if server.install_type == "docker":
            cmd = docker_cmd_build(server) + cmd

        if should_use_ssh(server):
            run_cmd_ssh(cmd, server)
        else:
            run_cmd_popen(cmd, server.id)

        proc_info = get_process(server.id, create=True)

        if proc_info.exit_status > 0:
            resp_dict = {"Error": "Refresh cmd failed!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=503, mimetype="application/json"
            )
            return response

        resp_dict = {"Success": "Output updated!"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
        )
        return response

api.add_resource(UpdateConsole, "/update-console/<string:server_id>")


######### API Server Statuses #########

class ServerStatus(Resource):
    @login_required
    def get(self, server_id):
        server = GameServer.query.filter_by(id=server_id).first()
        if server == None:
            resp_dict = {"Error": "Invalid id"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
            )
            return response

        if not user_has_permissions(current_user, "server-statuses", server.id):
            resp_dict = {"Error": "Permission Denied!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
            )
            return response

        server_status = get_server_status(server)
        resp_dict = {"id": server.id, "status": server_status}
        current_app.logger.info(log_wrap("resp_dict", resp_dict))

        response = Response(
            json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
        )
        return response

api.add_resource(ServerStatus, "/server-status/<string:server_id>")


######### API System Usage #########

class SystemUsage(Resource):
    @login_required
    def get(self):
        server_stats = get_server_stats()
        response = Response(
            json.dumps(server_stats, indent=4), status=200, mimetype="application/json"
        )
        return response

api.add_resource(SystemUsage, "/system-usage")


######### API CMD Output #########

class CmdOutput(Resource):
    @login_required
    def get(self, server_id):
        # Can't do anything if we don't have proc info vessel stored.
        if server_id not in get_all_processes():
            resp_dict = {"Error": "eer never heard of em"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
            )
            return response

        if not user_has_permissions(current_user, "cmd-output", server_id):
            resp_dict = {"Error": "Permission Denied!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
            )
            return response

        output = get_process(server_id, create=True)

        # Returns json for used by ajax code on /controls route.
        response = Response(output.toJSON(), status=200, mimetype="application/json")
        return response

api.add_resource(CmdOutput, "/cmd-output/<string:server_id>")


######### API GameServer Delete #########

class GameServerDelete(Resource):
    @login_required
    def delete(self, server_id):
        server = GameServer.query.filter_by(id=server_id).first()
        if server == None:
            resp_dict = {"Error": "Server not found!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=404, mimetype="application/json"
            )
            return response

        server_name = server.install_name

        config = read_config("delete")
        current_app.logger.info(log_wrap("config", config))

        # NOTE: For everyone's safety, if config options are incongruous, default
        # to safer keep user, keep files option. (ie. If delete_user is True and
        # remove_files is False, default to keep user.
        if config["delete_user"] and not config["remove_files"]:
            config["delete_user"] = False

        # Check if user has permissions to delete route & server.
        if not user_has_permissions(current_user, "delete", server_id):
            resp_dict = {
                "Error": f"Insufficient permission to delete {server.install_name}"
            }
            response = Response(
                json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
            )
            return response

        current_app.logger.info(log_wrap(f"{current_user} deleting ID: ", server_id))

        current_app.logger.info(server)

        # Drop any saved proc_info objects.
        remove_process(server_id)

        # Log to ensure process was dropped.
        current_app.logger.info(log_wrap("All processes", get_all_processes()))

        if not delete_server(server, config["remove_files"], config["delete_user"]):
            resp_dict = {
                "Error": "Problem deleting server, see error logs for more details."
            }
            response = Response(
                json.dumps(resp_dict, indent=4), status=500, mimetype="application/json"
            )
            return response

        # We don't want to keep deleted servers in the cache.
        update_tmux_socket_name_cache(server_id, None, True)
        delete_user = str(config["delete_user"])
        remove_files = str(config["remove_files"])
        audit_log_event(current_user.id, f"User '{current_user.username}', deleted game server '{server_name}', delete_user: {delete_user}, remove_file:{remove_files}")

        return "", 204

api.add_resource(GameServerDelete, "/delete/<string:server_id>")

