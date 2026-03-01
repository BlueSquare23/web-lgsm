import json
import getpass

from flask_login import login_required, current_user
from flask import (
    render_template,
    request,
    flash,
    url_for,
    redirect,
    current_app,
)

from app.utils import *
from app.forms.views import ValidateID, AddForm
from app.services import SudoersService
from app.container import container

# Constants.
USER = getpass.getuser()

from . import main_bp

######### Add Page #########

@main_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    # Check if user has permissions to add route.
    if not container.check_user_access().execute(current_user.id, "add"):
        flash("Your user does not have access to this page", category="error")
        return redirect(url_for("main.home"))

    server_json = None
    status_code = 200
    game_servers = container.list_game_servers().execute()
    form = AddForm()

    if request.method == "GET":

        if request.args:
            # Checking server id is valid.
            id_form = ValidateID(request.args)
            if not id_form.validate():
                validation_errors(id_form)
                return redirect(url_for("main.home"))

            server_id = request.args.get("server_id")
            server = container.get_game_server().execute(server_id)
            server = server.__dict__
            server_json = json.dumps(server)
            current_app.logger.info(log_wrap("server_json", server_json))

        return render_template(
            "add.html",
            user=current_user,
            server_json=server_json,
            game_servers=game_servers,
            form=form
        ), status_code

    # Handle Invalid form submissions.
    if not form.validate_on_submit():
        validation_errors(form)
        return redirect(url_for("main.add"))

    # Set default form username if none provided.
    username = form.username.data
    if not username:
        username = USER

    # Process form submissions.
    server = {
        'id': form.server_id.data,
        'install_name': form.install_name.data,
        'install_path': form.install_path.data,
        'script_name': form.script_name.data,
        'username': username,
        'install_type': form.install_type.data,
        'install_host': form.install_host.data,
        'install_finished': True,  # All server adds/edits are auto marked finished.
    }

    # Does the server already exist?
    new_server = True
    if container.get_game_server().execute(server['id']):
        new_server = False

    # Log & set GameServer obj vars after most of the validation is done.
    current_app.logger.info(log_wrap("server", server))

    if server['install_type'] == 'remote':
        if not server['install_host']: 
            flash("Missing required form field(s)!", category="error")
            return render_template("add.html",
                    user=current_user,
                    server_json=server_json,
                    game_servers=game_servers,
                    form=form
                ), 400

        if not is_ssh_accessible(server['install_host']):
            flash("Server does not appear to be SSH accessible!", category="error")
            return render_template("add.html",
                    user=current_user,
                    server_json=server_json,
                    game_servers=game_servers,
                    form=form
                ), 400

    if server['install_type'] == 'local':
        server['install_host'] = '127.0.0.1'

        if get_uid(server['username']) == None:
            flash("User not found on system!", category="error")
            return redirect(url_for("main.add"))

    if server['install_type'] == 'docker' and new_server:
        flash(
            f"For docker installs be sure to add the following sudoers rule to /etc/sudoers.d/{USER}-docker"
        )
        flash(
            f"{USER} ALL=(root) NOPASSWD: /usr/bin/docker exec --user {server.username} {server.script_name} *"
        )

    # TODO: For remote installs, generate an SSH key as part of add step.
    # Should probably even make form take existing SSH key file path as arg for
    # remote installs.

    container.edit_game_server().execute(**server)

    # Update web user's permissions to give access to new game server after adding it.
    if current_user.role != "admin":
        user_perms = json.loads(current_user.permissions)
        user_perms["server_ids"].append(server.id)
        current_user.permissions = json.dumps(user_perms)
        current_app.logger.info(
            log_wrap("Updated User Permissions:", user_ident.permissions)
        )
        # TODO: Clean this up I don't like passing from current user cause its an sql alch model. Also does this even work?
        container.edit_user.execute(**current_user.__dict__)

    # Auto add sudoers rule for server.
    if server['install_type'] == 'local' and server['username'] != USER:
        sudoers_service = SudoersService(username)
        if not sudoers_service.has_access():
            if not sudoers_service.add_user():
                flash(f"Please add following rule to give web-lgsm user access to server:\n/etc/sudoers.d/{USER}-{username}\n{USER} ALL=({username}) NOPASSWD: ALL")

    flash("Game server added!")
    container.log_audit_event().execute(current_user.id,  f"User '{current_user.username}', added game server '{server['install_name']}' with server_id {server['id']}")
    return redirect(url_for("main.home"))


