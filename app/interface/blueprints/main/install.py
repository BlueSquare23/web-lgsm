import os
import json
import getpass

from threading import Thread
from flask_login import login_required, current_user
from flask import (
    jsonify,
    render_template,
    request,
    flash,
    url_for,
    redirect,
    current_app,
)

from app.utils import *
from app.interface.forms import AddForm, validation_errors

# Constants.
CWD = os.getcwd()
USER = getpass.getuser()
VENV = "/opt/web-lgsm/"
from app.utils.paths import PATHS

from app.interface.use_cases import get_template_config, check_user_access, list_installable_game_servers, check_and_get_lgsmsh, list_running_game_server_installs, get_game_server, get_process, cancel_game_server_install, query_game_server, edit_game_server, get_user, edit_user, run_command, clear_install_buffer_output, log_audit_event

from . import main_bp

######### Install Page #########

@main_bp.route("/install", methods=["GET", "POST"])
@login_required
def install():
    config = get_template_config()

    # Check if user has permissions to install route.
    if not check_user_access(current_user.id, "install"):
        flash("Your user does not have access to this page", category="error")
        return redirect(url_for("main.home"))

    # Pull in install server list from game_servers.json file.
    install_list = list_installable_game_servers()
    if not install_list:
        flash("Error loading game_servers.json file!", category="error")
        return redirect(url_for("main.home"))

    # Initialize blank install_name, used for update-text-area.js.
    install_name = ""

    # Check for / install the main linuxgsm.sh script.
    lgsmsh = "linuxgsm.sh"
    check_and_get_lgsmsh(f"bin/{lgsmsh}")

    # Check if any installs are currently running.
    running_installs = list_running_game_server_installs()

    form = AddForm()

    if request.method == "GET":
        server_id = request.args.get("server_id")
        cancel = request.args.get("cancel")
        if server_id != None and cancel == "true":
            server = get_game_server(server_id)
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
            proc_info = get_process(server.id)

            current_app.logger.info(log_wrap("proc_info", proc_info))

            if proc_info.pid:
                success = cancel_game_server_install(proc_info.pid)
                if success:
                    flash("Installation Canceled!")
                else:
                    flash("Problem canceling installation!", category="error")

        # For displaying Installing ServerName...
        if server_id != None:
            server = get_game_server(server_id)
            if server == None:
                flash(
                    "Can't get details for server.",
                    category="error",
                )
                return redirect(url_for("main.install"))

            install_name = server.install_name

        return render_template(
            "install.html",
            user=current_user,
            web_lgsm_user=USER,
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

# For debug
#    return jsonify(form.data)
    current_app.logger.debug(jsonify(form.data))

    # Form data.
    install_name = form.install_name.data
    install_path = form.install_path.data
    install_type = 'local'  # Hardcode to local for now is fine.
    script_name = form.script_name.data
    username = form.username.data

    # Just to be doubly sure.
    install_name = install_name.replace(" ", "_").replace(":", "")

    game_server = {
        "id": None,  # New game server dont have IDs yet.
        "install_name": install_name,
        "install_path": install_path,
        "install_type": install_type,
        "script_name": script_name,
        "username": username
    }

    # If install already exists.
    if query_game_server(**game_server):
        current_app.logger.debug(log_wrap('Install Already Exists!', game_server))
        flash("An installation with those details already exits!", category="error")
        return redirect(url_for("main.install"))

    # Add server to DB.
    server_id = edit_game_server(**game_server)
    if not server_id:
        flash("Problem adding installation details to database", category="error")
        return redirect(url_for("main.install"))

    current_app.logger.info(log_wrap("server_id", server_id))

    # Update web user's permissions to give access to new game server post install.
    if current_user.role != "admin":
        user_perms = json.loads(current_user.permissions)
        user_perms["server_ids"].append(server_id)

#        current_user.permissions = json.dumps(user_perms)

        user = get_user(current_user.id)
        user.permissions = json.dumps(user_perms)

        edit_user(**user.__dict__)

    #TODO: Move into install manager to launch install.
    cmd = [
        PATHS["sudo"],
        "-n",
        os.path.join(VENV, "bin/python"),
        PATHS["ansible_connector"],
        "--install",
        str(server_id),
    ]

    install_daemon = Thread(
        target=run_command,
        args=(cmd, None, server_id, current_app.app_context()),
        daemon=True,
        name=f"web_lgsm_install_{server_id}",
    )
    install_daemon.start()

    clear_daemon = Thread(
        target=clear_install_buffer_output,
        args=(server_id, current_app.app_context()),
        daemon=True,
        name=f"clear_install_{server_id}",
    )
    clear_daemon.start()

    log_audit_event(current_user.id,  f"User '{current_user.username}', installed game server '{install_name}'")

    return render_template(
        "install.html",
        user=current_user,
        web_lgsm_user=USER,
        servers=install_list,
        _config=config,
        install_name=install_name,
        server_id=server_id,
        running_installs=running_installs,
        form=form,
    )

