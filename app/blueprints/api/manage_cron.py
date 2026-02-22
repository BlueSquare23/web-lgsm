import json

from flask import Response, jsonify, request
from flask_login import login_required, current_user
from flask_restful import Resource
from cron_converter import Cron
from werkzeug.datastructures import MultiDict

from app.utils import *
from app.forms.views import ValidateID

from . import api

from app.container import container

######### API Cron Manager #########

class ManageCron(Resource):
    def check_perms(self):
        if not current_user.has_access("jobs"):
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

    @login_required
    def get(self, server_id, job_id=None):
        allowed, resp = self.check_perms()
        if not allowed:
            return resp

        valid, resp = self.validate_server_id(server_id)
        if not valid:
            return resp

        jobs_list = container.list_cron_jobs().execute()

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

        valid, resp = self.validate_server_id(server_id)
        if not valid:
            return resp

        data = request.json
#        cron = CronService(server_id)

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
            'job_id': job_id,
            'server_id': server_id,
            'command': command,
            'comment': comment,
            'schedule': cron_expression,
        }

#        if cron.edit_job(job):
        if container.update_cron_job().execute(**job):
            return {'success':'job updated'}, 201
        else:
            return {'error':'problem updating job'}, 500

    @login_required
    def delete(self, server_id, job_id):
        allowed, resp = self.check_perms()
        if not allowed:
            return resp

        valid, resp = self.validate_server_id(server_id)
        if not valid:
            return resp

#        cron = CronService(server_id)
#        if cron.delete_job(job_id):
        if container.delete_cron_job().execute(job_id):
            audit_log_event(current_user.id, f"User '{current_user.username}', deleted job_id '{job_id}' for server_id '{server_id}'")
            return '', 204

        return {'error':'unable to remove job'}, 500

api.add_resource(
    ManageCron,
    "/cron/<string:server_id>",
    "/cron/<string:server_id>/<string:job_id>"
)

