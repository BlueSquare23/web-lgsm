import json

from flask import Response
from flask_login import login_required, current_user
from flask_restful import Resource

from app.utils import *

from . import api

from app.interface.use_cases import list_processes, check_user_access, get_process

######### API CMD Output #########

class CmdOutput(Resource):
    @login_required
    def get(self, server_id):

        # Can't do anything if we don't have proc info vessel stored.
        if server_id not in list_processes():
            resp_dict = {"Error": "eer never heard of em"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
            )
            return response

        if not check_user_access(current_user.id, "cmd-output", server_id):
            resp_dict = {"Error": "Permission Denied!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
            )
            return response

        proc_info = get_process(server_id, create=True)

        # Returns json for used by ajax code on /controls route.
        response = Response(proc_info.toJSON(), status=200, mimetype="application/json")
        return response

api.add_resource(CmdOutput, "/cmd-output/<string:server_id>")

