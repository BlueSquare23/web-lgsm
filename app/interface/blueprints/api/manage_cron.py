import json

from flask import Response, jsonify, request
from flask_login import login_required, current_user
from flask_restful import Resource
from cron_converter import Cron
from werkzeug.datastructures import MultiDict

from app.utils import *
from app.interface.forms import ValidateID

from . import api

from app.interface.use_cases import check_user_access, list_cron_jobs, update_cron_job, delete_cron_job, log_audit_event

######### API Cron Manager #########

class ManageCron(Resource):
    def check_perms(self, server_id=None):
        if not check_user_access(current_user.id, "jobs", server_id):
            resp_dict = { "Error": f"Insufficient permission" }
            response = Response(
                json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
            )
            return (False, response)
        return (True, None)

    def validate_server_id(self, server_id):
        id_form = ValidateID( MultiDict([('server_id', server_id)]) )
        if not id_form.validate():
            return (False, ('Not found', 404))

        return (True, None)

    # TODO: This works for now. But eventually just add usecase for get_job
    # from the repository and do this that way instead.
    @login_required
    def get(self, server_id, job_id=None):
        valid, resp = self.validate_server_id(server_id)
        if not valid:
            return resp

        allowed, resp = self.check_perms(server_id)
        if not allowed:
            return resp

        jobs_list = list_cron_jobs(server_id)

        if job_id:
            for job in jobs_list:
                if job.server_id == server_id and job.job_id == job_id:
                    return jsonify(job.__dict__)
            return ('Not found', 404)

        return jsonify(jobs_list)

    @login_required
    def post(self, server_id, job_id=None):
        valid, resp = self.validate_server_id(server_id)
        if not valid:
            return resp

        allowed, resp = self.check_perms(server_id)
        if not allowed:
            return resp

        data = request.json
        command = data.get('command')
        custom = data.get('custom')
        comment = data.get('comment')
        schedule = data.get('schedule')

        try:
            Cron(schedule)
        except ValueError:
            return {'Error':'Invalid cron schedule'}, 400

        if command == 'send':
            command = f"send {custom}"

        if command == 'custom':
            command = f"custom: {custom}"

        job = {
            'job_id': job_id,
            'server_id': server_id,
            'command': command,
            'comment': comment,
            'schedule': schedule,
        }

        if update_cron_job(**job):
            return {'success':'job updated'}, 201
        else:
            return {'error':'problem updating job'}, 500

    @login_required
    def delete(self, server_id, job_id):
        valid, resp = self.validate_server_id(server_id)
        if not valid:
            return resp

        allowed, resp = self.check_perms(server_id)
        if not allowed:
            return resp

        if delete_cron_job(job_id):
            log_audit_event(current_user.id, f"User '{current_user.username}', deleted job_id '{job_id}' for server_id '{server_id}'")
            return '', 204

        return {'error':'unable to remove job'}, 500

api.add_resource(
    ManageCron,
    "/cron/<string:server_id>",
    "/cron/<string:server_id>/<string:job_id>"
)

