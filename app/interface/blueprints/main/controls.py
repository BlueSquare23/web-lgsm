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

from app.utils import *
from app.interface.forms import validation_errors, ValidateID, SendCommandForm, ServerControlForm, SelectCfgForm
from app import cache

from app.interface.use_cases import get_template_config, query_game_server, get_game_server, check_user_access, check_sudoers_access, add_sudoers_rule, list_controls, getboolean_config, find_cfg_paths, get_game_server_power_state, log_audit_event, run_command, list_controls

from . import main_bp

# Constants.
USER = getpass.getuser()

######### Controls Page #########

@main_bp.route("/controls", methods=["GET", "POST"])
@login_required
def controls():
    config = get_template_config()

    # Initialize forms
    send_cmd_form = SendCommandForm()
    controls_form = ServerControlForm()
    select_cfg_form = SelectCfgForm()

    if request.method == "GET":
        # Serve a redirect to id for server_name because its nice :)
        server_name = request.args.get("server")
        if server_name:
            current_app.logger.info(log_wrap("server_name", server_name))
            game_server_data = {'install_name': server_name}
            server = query_game_server(**game_server_data)
            current_app.logger.info(log_wrap("server", server))
            if server == None:
                flash("Invalid game server name!", category="error")
                return redirect(url_for("main.home"))

            return redirect(url_for("main.controls", server_id=server.id))

        # Checking id is valid.
        id_form = ValidateID(request.args)
        if not id_form.validate():
            validation_errors(id_form)
            return redirect(url_for("main.home"))

        server_id = request.args.get("server_id")
        server = get_game_server(server_id)
        current_app.logger.info(log_wrap("server_id", server_id))
        jobs_edit = True if server.install_type == 'local' else False

        # Check if user has permissions to game server for controls route.
        if not check_user_access(current_user.id, "controls", server_id):
            flash("Your user does not have access to this server", category="error")
            return redirect(url_for("main.home"))

        # TODO: REPLACE THIS WHEN I REPLACE THIS IN ADD
        # Auto add sudoers rule for server if it doesn't have one, for backwards compat.
        if server.install_type == 'local' and server.username != USER:
            if not check_sudoers_access(server.username):
                if not add_sudoers_rule(server.username):
                    flash(f"Please add following rule to give web-lgsm user access to server:\n/etc/sudoers.d/{USER}-{server.username}\n{USER} ALL=({server.username}) NOPASSWD: ALL")

        # Pull in controls list from controls.json file.
        controls_list = list_controls(server.script_name, current_user)
        current_app.logger.debug(controls_list)

        if server.install_type == "remote":
            if not is_ssh_accessible(server.install_host):
                flash("Unable to access remote server over ssh!", category="error")
                return redirect(url_for("main.home"))

        elif server.install_type == "local" and server.username == USER and not os.path.isdir(server.install_path):
            flash("No game server installation directory found!", category="error")
            return redirect(url_for("main.home"))

        # Cfg editor buttons stuff.
        cache_key = f"cfg_paths_{server_id}"
        cfg_paths = cache.get(cache_key)

        if not getboolean_config("settings","file_manager"):
            cfg_paths = []

        elif cfg_paths is None:  # Not in cache.
            current_app.logger.info("Getting cfg_paths")
            cfg_paths = find_cfg_paths(server)

            # Wtf, I don't remember this return "failed" but whatever..
            if cfg_paths == "failed":
                flash("Error reading accepted_cfgs.json!", category="error")
                cfg_paths = []

            cache.set(cache_key, cfg_paths, timeout=1800)

        cfg_paths = find_cfg_paths(server)
        current_app.logger.info(log_wrap("cfg_paths", cfg_paths))
        current_app.logger.info(log_wrap("controls_list", controls_list))

        return render_template(
            "controls.html",
            user=current_user,
            server_id=server_id,
            server_name=server.install_name,
            show_jobs_edit=jobs_edit,
            server_controls=controls_list,
            _config=config,
            cfg_paths=cfg_paths,
            select_cfg_form=select_cfg_form,
            controls_form=controls_form,
            send_cmd_form=send_cmd_form,
        )

    # Handle POST requests.
    if controls_form.ctrl_form.data:
        if not controls_form.validate_on_submit():
            validation_errors(controls_form)
            return redirect(url_for("main.home"))

        server_id = controls_form.server_id.data
        short_ctrl = controls_form.control.data

    elif send_cmd_form.send_form.data:
        if not send_cmd_form.validate_on_submit():
            validation_errors(send_cmd_form)
            return redirect(url_for("main.home"))

        server_id = send_cmd_form.server_id.data
        short_ctrl = send_cmd_form.control.data
        send_cmd = send_cmd_form.send_cmd.data

    else:
        flash("Invalid form submission!", category="error")
        return redirect(url_for("main.controls", server_id=server_id))

    server = get_game_server(server_id)
    current_app.logger.info(log_wrap("server_id", server_id))

    # TODO: Eventually find a way to move this into ServerControlForm class
    # validation. Problem is right now, not sure how to validate server id
    # first, then get server in order to run this validation. So this works for
    # rn.
    # Validate short_ctrl against contents of control.json file.
    if not valid_command(short_ctrl, server.script_name, current_user):
        flash("Invalid Command!", category="error")
        return redirect(url_for("main.controls", server_id=server_id))

    # Check if user has permissions to game server for controls route.
    if not check_user_access(current_user.id, "controls", server_id):
        flash("Your user does not have access to this server", category="error")
        return redirect(url_for("main.home"))

    # If file manager is disabled in the main.conf.
    if not config.getboolean('settings',"file_manager"):
        cfg_paths = []
    else:
        current_app.logger.info("Getting cfg_paths")
        cfg_paths = find_cfg_paths(server)

    current_app.logger.info(log_wrap("cfg_paths", cfg_paths))

    # Pull in controls list from controls.json file.
    controls_list = list_controls(server.script_name, current_user)

    if not controls_list:
        flash("Error loading controls.json file!", category="error")
        return redirect(url_for("main.home"))

    script_path = os.path.join(server.install_path, server.script_name)

    # Console option, use tmux capture-pane to get output.
    if short_ctrl == "c":
        active = get_game_server_power_state(server)
        if not active:
            flash("Server is Off! No Console Output!", category="error")
            return redirect(url_for("main.controls", server_id=server_id))

        jobs_edit = True if server.install_type == 'local' else False

        # Console mode is trigger in JS, set off by console=True. Nothing
        # for backend console happens here. See /api/update-console route!
        return render_template(
            "controls.html",
            user=current_user,
            server_id=server_id,
            server_name=server.install_name,
            server_controls=controls_list,
            show_jobs_edit=jobs_edit,
            _config=config,
            cfg_paths=cfg_paths,
            select_cfg_form=select_cfg_form,
            controls_form=controls_form,
            send_cmd_form=send_cmd_form,
            console=True,
        )

    elif short_ctrl == "sd":
        # Check if send_cmd is enabled in main.conf.
        if not config.getboolean('settings','send_cmd'):
            flash("Send command button disabled!", category="error")
            return redirect(url_for("main.controls", server_id=server_id))

        active = get_game_server_power_state(server)
        if not active:
            flash("Server is Off! Cannot send commands to console!", category="error")
            return redirect(url_for("main.controls", server_id=server_id))

        cmd = [script_path, short_ctrl, send_cmd]

        flash("Sending command to console")
        log_audit_event(current_user.id,  f"User '{current_user.username}', sent command '{send_cmd}' to '{server.install_name}'")

        if server.install_type == "docker":
            cmd = docker_cmd_build(server) + cmd

        daemon = Thread(
            target=run_command,
            args=(cmd, server, server.id, current_app.app_context()),
            daemon=True,
            name="ConsoleCMD",
        )
        daemon.start()
        return redirect(url_for("main.controls", server_id=server_id))

    else:
        cmd = [script_path, short_ctrl]

        # Get long_ctrl for matching short_ctrl for audit logging. 
        for control in controls_list:
            if control.short_ctrl == short_ctrl:
                long_ctrl = control.long_ctrl
                break

        log_audit_event(current_user.id, f"User '{current_user.username}', ran '{long_ctrl}' on '{server.install_name}'")

        if server.install_type == "docker":
            cmd = docker_cmd_build(server) + cmd

        daemon = Thread(
            target=run_command,
            args=(cmd, server, server.id, current_app.app_context()),
            daemon=True,
            name="Command",
        )
        daemon.start()
        return redirect(url_for("main.controls", server_id=server_id))

# TODO/NOTE: This can stay for now, but its on the chopping block. This
# validation should now be handled by flask-wtf/wtforms classes. Once I get
# this fixed up in the controls route, this can go.
def valid_command(ctrl, server, current_user):
    """
    Validates short commands from controls route form for game server. Some
    game servers may have specific game server command exemptions. This
    function basically just checks if supplied cmd is in list of accepted cmds
    from get_controls().

    Args:
        ctrl (str): Short ctrl string to validate.
        server (GameServer): Game server to check command against.
        current_user (LocalProxy): Currently logged in flask user object.

    Returns:
        bool: True if cmd is valid for user & game server, False otherwise.
    """

    controls = list_controls(server, current_user)
    for control in controls:
        # Aka is valid control.
        if ctrl == control.short_ctrl:
            return True

    return False

