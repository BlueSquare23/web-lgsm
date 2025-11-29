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

from app import db
from app.utils import *
from app.models import GameServer, User
from app.forms.views import ValidateID, AddForm

# Constants.
USER = getpass.getuser()

from . import main_bp

######### Add Page #########

@main_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    # Check if user has permissions to add route.
    if not user_has_permissions(current_user, "add"):
        return redirect(url_for("main.home"))

    server_json = None
    status_code = 200
    game_servers = GameServer.query.all()
    form = AddForm()

    if request.method == "GET":

        if request.args:
            # Checking server id is valid.
            id_form = ValidateID(request.args)
            if not id_form.validate():
                validation_errors(id_form)
                return redirect(url_for("main.home"))

            server_id = request.args.get("server_id")
            server = GameServer.query.filter_by(id=server_id).first()
            server = server.__dict__
            del(server["_sa_instance_state"])
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

    # Process form submissions.
    server_id = form.server_id.data
    install_name = form.install_name.data
    install_path = form.install_path.data
    script_name = form.script_name.data
    username = form.username.data
    install_type = form.install_type.data
    install_host = form.install_host.data

    if server_id == '' or server_id == None:
        new_server = True
        server = GameServer()
    else:
        new_server = False
        server = GameServer.query.filter_by(id=server_id).first()

    server.install_finished = True  # All server adds/edits are auto marked finished.

    # Set default user if none provided.
    if username == None or username == "":
        username = USER

    # Log & set GameServer obj vars after most of the validation is done.
    current_app.logger.info(log_wrap("install_name", install_name))
    current_app.logger.info(log_wrap("install_path", install_path))
    current_app.logger.info(log_wrap("script_name", script_name))
    current_app.logger.info(log_wrap("username", username))
    current_app.logger.info(log_wrap("install_type", install_type))
    current_app.logger.info(log_wrap("install_host", install_host))

    server.install_name = install_name
    server.install_path = install_path
    server.script_name = script_name
    server.username = username
    server.install_type = install_type

    if install_type == "remote":
        if install_host == None or install_host == "":
            flash("Missing required form field(s)!", category="error")
            return render_template("add.html",
                    user=current_user,
                    server_json=server_json,
                    game_servers=game_servers,
                    form=form
                ), 400

        if not is_ssh_accessible(install_host):
            flash("Server does not appear to be SSH accessible!", category="error")
            return render_template("add.html",
                    user=current_user,
                    server_json=server_json,
                    game_servers=game_servers,
                    form=form
                ), 400

        server.install_type = "remote"
        server.install_host = install_host

    if install_type == "local":
        server.install_type = "local"
        server.install_host = "127.0.0.1"

        if get_uid(username) == None:
            flash("User not found on system!", category="error")
            return redirect(url_for("main.add"))

    if install_type == "docker" and new_server:
        flash(
            f"For docker installs be sure to add the following sudoers rule to /etc/sudoers.d/{USER}-docker"
        )
        flash(
            f"{USER} ALL=(root) NOPASSWD: /usr/bin/docker exec --user {server.username} {server.script_name} *"
        )

    if should_use_ssh(server) and new_server:
        keyfile = get_ssh_key_file(username, server.install_host)
        if keyfile == None:
            flash(f"Problem generating new ssh keys!", category="error")
            return redirect(url_for("main.add"))

        flash(
            f"Add this public key: {keyfile}.pub to the remote server's ~{username}/.ssh/authorized_keys file!"
        )

    if new_server:
        db.session.add(server)

    db.session.commit()

    server = GameServer.query.filter_by(install_name=install_name).first()

    # Update web user's permissions to give access to new game server after adding it.
    if current_user.role != "admin":
        user_ident = User.query.filter_by(username=current_user.username).first()
        user_perms = json.loads(user_ident.permissions)
        user_perms["server_ids"].append(server.id)
        user_ident.permissions = json.dumps(user_perms)
        current_app.logger.info(
            log_wrap("Updated User Permissions:", user_ident.permissions)
        )
        db.session.commit()

    flash("Game server added!")
    audit_log_event(current_user.id, f"User '{current_user.username}', added game server '{install_name}' with server_id {server.id}")
    return redirect(url_for("main.home"))


