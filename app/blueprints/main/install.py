import os
import json
import getpass

from threading import Thread
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
from app.models import User, GameServer
from app.services import ProcInfoService
from app.forms.views import InstallForm, AddForm

# Constants.
CWD = os.getcwd()
USER = getpass.getuser()
VENV = "/opt/web-lgsm/"
from app.utils.paths import PATHS

from app.config.config_manager import ConfigManager

from app.services import CommandExecService

from . import main_bp

######### Install Page #########

@main_bp.route("/install", methods=["GET", "POST"])
@login_required
def install():
    config = ConfigManager()
    command_service = CommandExecService(config)

    # Check if user has permissions to install route.
    if not current_user.has_access("install"):
        flash("Your user does not have access to this page", category="error")
        return redirect(url_for("main.home"))

    # Pull in install server list from game_servers.json file.
    install_list = get_servers()
    if not install_list:
        flash("Error loading game_servers.json file!", category="error")
        return redirect(url_for("main.home"))

    # Initialize blank install_name, used for update-text-area.js.
    install_name = ""

    # Check for / install the main linuxgsm.sh script.
    lgsmsh = "linuxgsm.sh"
    check_and_get_lgsmsh(f"bin/{lgsmsh}")

    # Check if any installs are currently running.
    running_installs = get_running_installs()

    form = AddForm()

    if request.method == "GET":
        server_id = request.args.get("server_id")
        cancel = request.args.get("cancel")
        if server_id != None and cancel == "true":
            server = GameServer.query.filter_by(id=server_id).first()
            if server == None:
                flash(
                    "Problem canceling installation! Game server id not found.",
                    category="error",
                )
                return redirect(url_for("main.install"))

            # Check if install thread is still running.
            if server.id not in running_installs:
                flash(
                    "Install for server not currently running!",
                    category="error",
                )
                return redirect(url_for("main.install"))

            # Log proc info so can see what's going on.
            proc_info = ProcInfoService().get_process(server.id)
            current_app.logger.info(log_wrap("proc_info", proc_info))

            if proc_info.pid:
                success = cancel_install(proc_info.pid)
                if success:
                    flash("Installation Canceled!")
                else:
                    flash("Problem canceling installation!", category="error")

        return render_template(
            "install.html",
            user=current_user,
            web_lgsm_user = USER,
            servers=install_list,
            install_name=install_name,
            server_id=server_id,
            _config=config,
            running_installs=running_installs,
            create_new_user=config.getboolean('settings','install_create_new_user'),
            form=form,
        )

    # Handle POSTs

    # Handle Invalid form submissions.
    if not form.validate_on_submit():
        validation_errors(form)
        return redirect(url_for("main.install"))

#    from flask import jsonify
#    return jsonify(form.data)

    # Form data.
    install_name = form.install_name.data
    install_path = form.install_path.data
    install_type = 'local'  # Hardcode to local for now is fine.
    script_name = form.script_name.data
    username = form.username.data

    # Just to be doubly sure.
    install_name = install_name.replace(" ", "_")
    install_name = install_name.replace(":", "")

    install_exists = GameServer.query.filter_by(
        install_name=install_name,
        install_path=install_path,
        install_type=install_type,
        script_name=script_name,
        username=username
    ).first()

    if install_exists:
        flash("An installation with those details already exits.", category="error")
        return redirect(url_for("main.install"))

    server = GameServer()
    server.install_name = install_name
    server.install_path = install_path
    server.script_name = script_name
    server.username = username
    server.is_container = False
    server.install_type = install_type
    server.install_host = "127.0.0.1"
    server.install_finished = False
    server.keyfile_path = ""

    current_app.logger.info(log_wrap("server", server))

    # Add the install to the database.
    db.session.add(server)
    db.session.commit()

    server_id = GameServer.query.filter_by(install_name=install_name).first().id

    current_app.logger.info(log_wrap("server_id", server_id))

    # Update web user's permissions to give access to new game server post install.
    if current_user.role != "admin":
        user_ident = User.query.filter_by(username=current_user.username).first()
        user_perms = json.loads(user_ident.permissions)
        user_perms["server_ids"].append(server_id)
        user_ident.permissions = json.dumps(user_perms)
        db.session.commit()

    cmd = [
        PATHS["sudo"],
        "-n",
        os.path.join(VENV, "bin/python"),
        PATHS["ansible_connector"],
        "--install",
        str(server_id),
    ]

    current_app.logger.info(log_wrap("cmd", cmd))
    current_app.logger.info(log_wrap("all processes", ProcInfoService().get_all_processes()))

    install_daemon = Thread(
        target=command_service.run_command,
        args=(cmd, None, server.id, current_app.app_context()),
        daemon=True,
        name=f"web_lgsm_install_{server_id}",
    )
    install_daemon.start()

    clear_daemon = Thread(
        target=clear_proc_info_post_install,
        args=(server_id, current_app.app_context()),
        daemon=True,
        name=f"clear_install_{server_id}",
    )
    clear_daemon.start()

    audit_log_event(current_user.id, f"User '{current_user.username}', installed game server '{server.install_name}'")

    return render_template(
        "install.html",
        user=current_user,
        servers=install_list,
        _config=config,
        install_name=install_name,
        server_id=server_id,
        running_installs=running_installs,
        form=form,
    )

