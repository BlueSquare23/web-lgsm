import json

from flask import Response
from flask_login import login_required, current_user
from flask_restful import Resource

from app.utils import *
from app.services import ProcInfoService

from . import api

######### API CMD Output #########

class CmdOutput(Resource):
    @login_required
    def get(self, server_id):
        proc_service = ProcInfoService()

        # Can't do anything if we don't have proc info vessel stored.
        if server_id not in proc_service.get_all_processes():
            resp_dict = {"Error": "eer never heard of em"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
            )
            return response

        if not current_user.has_access("cmd-output", server_id):
            resp_dict = {"Error": "Permission Denied!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
            )
            return response

        proc_info = proc_service.get_process(server_id, create=True)

        # Returns json for used by ajax code on /controls route.
        response = Response(proc_info.toJSON(), status=200, mimetype="application/json")
        return response

api.add_resource(CmdOutput, "/cmd-output/<string:server_id>")

