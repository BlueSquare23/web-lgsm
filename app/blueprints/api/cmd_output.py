import json

from flask import Response
from flask_login import login_required, current_user
from flask_restful import Resource

from app.utils import *
from app.processes_global import *

from . import api


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

