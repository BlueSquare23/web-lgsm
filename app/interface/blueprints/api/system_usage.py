import json

from flask import Response
from flask_login import login_required
from flask_restful import Resource

from app.container import container

from . import api

######### API System Usage #########

class SystemUsage(Resource):
    @login_required
    def get(self):
        server_stats = container.get_host_stats().execute()
        response = Response(
            json.dumps(server_stats, indent=4), status=200, mimetype="application/json"
        )
        return response

api.add_resource(SystemUsage, "/system-usage")

