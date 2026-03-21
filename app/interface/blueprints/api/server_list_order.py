import json

from flask import Response, request, current_app
from flask_login import login_required, current_user
from flask_restful import Resource

from app.utils.helpers import log_wrap

from . import api

from app.container import container

######### API Server Listing Order #########

class ServerListOrder(Resource):
    @login_required
    def post(self):
        data = request.json
        order = data.get('order')

        if not order:
            return {'Error':'Invalid order data'}, 400

        current_app.logger.debug(log_wrap("order", order))

        for index, item in enumerate(order):

            server = container.get_game_server().execute(item['id'])
            server.sort_order = index

            current_app.logger.debug(log_wrap("server", server))

            if not container.edit_game_server().execute(**server.__dict__):
                return {'Error':'Problem updating GameServer sort_order'}, 500

        resp_dict = {"success": "Sort order updated successfully"} 
        current_app.logger.info(log_wrap("resp_dict", resp_dict))

        response = Response(
            json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
        )
        return response

api.add_resource(ServerListOrder, "/update-order")

