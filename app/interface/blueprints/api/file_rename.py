import json

from urllib.parse import unquote

from flask import Response, request, current_app
from flask_login import login_required, current_user
from flask_restful import Resource

from . import api

from app.utils import log_wrap

from app.interface.use_cases import log_audit_event, get_game_server, check_user_access, rename_file, is_filename_length_valid


######### API File Rename #########

class FileRename(Resource):
    @login_required
    def post(self, server_id, file_path):
        server = get_game_server(server_id)
        if server == None:
            resp_dict = {"Error": "Server not found!"}
            return Response(json.dumps(resp_dict, indent=4), status=404, mimetype="application/json")

        # Try unwrap path url encoding
        try:
            file_path = unquote(file_path)
        except Exception as e:
            resp_dict = {"Error": f"Problem unwrapping path url encoding: {e}"}
            return Response(json.dumps(resp_dict, indent=4), status=400, mimetype="application/json")

        # Get new name from request body
        data = request.get_json()
        if not data or "new_name" not in data:
            resp_dict = {"Error": "Missing new_name in request body"}
            return Response(json.dumps(resp_dict, indent=4), status=400, mimetype="application/json")

        new_name = data["new_name"]

        # Sanitize filename
        new_name = secure_filename(name)

        valid, error = is_filename_length_valid(new_name, 100)
        if not valid:
            resp_dict = {"Error": error}
            return Response(json.dumps(resp_dict, indent=4), status=400, mimetype="application/json")

        # Check permissions
        if not check_user_access(current_user.id, "files_edit", server_id):
            resp_dict = {
                "Error": f"Insufficient permission to rename files for {server.install_name}"
            }
            return Response(json.dumps(resp_dict, indent=4), status=403, mimetype="application/json")

        current_app.logger.info(log_wrap(f"{current_user} renaming {file_path} -> {new_name}: ", server_id))

        if rename_file(server, file_path, new_name):
            log_audit_event(current_user.id, f"User '{current_user.username}', renamed file '{file_path}' to '{new_name}'")
            return "", 204
        else:
            resp_dict = {"Error": "Problem renaming file"}
            return Response(json.dumps(resp_dict, indent=4), status=500, mimetype="application/json")


api.add_resource(FileRename, "/files/rename/<string:server_id>/<string:file_path>")
