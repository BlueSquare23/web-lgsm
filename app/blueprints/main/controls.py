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
from app.models import GameServer
from app.forms.views import ValidateID, SendCommandForm, ServerControlForm, SelectCfgForm
from app.services import ControlService, CommandExecService
from app import cache

from app.config.config_manager import ConfigManager

from . import main_bp

######### Controls Page #########

@main_bp.route("/controls", methods=["GET", "POST"])
@login_required
def controls():
    config = ConfigManager()
    controls_service = ControlService()
    command_service = CommandExecService(config)

    # Initialize forms
    send_cmd_form = SendCommandForm()
    controls_form = ServerControlForm()
    select_cfg_form = SelectCfgForm()

    if request.method == "GET":
        # Serve a redirect to id for server_name because its nice :)
        server_name = request.args.get("server")
        if server_name:
            current_app.logger.info(log_wrap("server_name", server_name))
            server = GameServer.query.filter_by(install_name=server_name).first()
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
        server = GameServer.query.filter_by(id=server_id).first()
        current_app.logger.info(log_wrap("server_id", server_id))
        jobs_edit = True if server.install_type == 'local' else False

        # Check if user has permissions to game server for controls route.
        if not current_user.has_access("controls", server_id):
            flash("Your user does not have access to this server", category="error")
            return redirect(url_for("main.home"))

        # Pull in controls list from controls.json file.
        controls_list = controls_service.get_controls(server.script_name, current_user)
        current_app.logger.debug(controls_list)

        if should_use_ssh(server):
            if not is_ssh_accessible(server.install_host):
                if server.install_type == "remote":
                    flash("Unable to access remote server over ssh!", category="error")
                    return redirect(url_for("main.home"))
                else:
                    flash("Unable to access local install over ssh!", category="error")
                    return redirect(url_for("main.home"))

        elif server.install_type == "local" and not os.path.isdir(server.install_path):
            flash("No game server installation directory found!", category="error")
            return redirect(url_for("main.home"))

        # Cfg editor buttons stuff.
        cache_key = f"cfg_paths_{server_id}"
        cfg_paths = cache.get(cache_key)

        if not config.getboolean("settings","cfg_editor"):
            cfg_paths = []

        elif cfg_paths is None:  # Not in cache.
            current_app.logger.info("Getting cfg_paths")

            from app.services import CfgManagerService
            #TODO: UPDATE THIS HARDCODED STRING WHEN YOU'RE DONE YOU FRICKIN IDIOT!!!
            cfg_manager = CfgManagerService('/home/blue/Projects/web-lgsm/app/utils/')
            cfg_paths = cfg_manager.find_cfg_paths(server)

            if cfg_paths == "failed":
                flash("Error reading accepted_cfgs.json!", category="error")
                cfg_paths = []

            cache.set(cache_key, cfg_paths, timeout=1800)

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

    server = GameServer.query.filter_by(id=server_id).first()
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
    if not current_user.has_access("controls", server_id):
        flash("Your user does not have access to this server", category="error")
        return redirect(url_for("main.home"))

    # If cfg editor is disabled in the main.conf.
    if not config.getboolean('settings',"cfg_editor"):
        cfg_paths = []
    else:
        current_app.logger.info("Getting cfg_paths")

        from app.services import CfgManagerService
        #TODO: UPDATE THIS HARDCODED STRING WHEN YOU'RE DONE YOU FRICKIN IDIOT!!!
        cfg_manager = CfgManagerService('/home/blue/Projects/web-lgsm/app/utils/')
        cfg_paths = cfg_manager.find_cfg_paths(server)

    current_app.logger.info(log_wrap("cfg_paths", cfg_paths))

    # Pull in controls list from controls.json file.
    controls_list = controls_service.get_controls(server.script_name, current_user)

    if not controls_list:
        flash("Error loading controls.json file!", category="error")
        return redirect(url_for("main.home"))

    script_path = os.path.join(server.install_path, server.script_name)

    # Console option, use tmux capture-pane to get output.
    if short_ctrl == "c":
        active = get_server_status(server)
        if not active:
            flash("Server is Off! No Console Output!", category="error")
            return redirect(url_for("main.controls", server_id=server_id))

        # Console mode is trigger in JS, set off by console=True. Nothing
        # for backend console happens here. See /api/update-console route!
        return render_template(
            "controls.html",
            user=current_user,
            server_id=server_id,
            server_name=server.install_name,
            server_controls=controls_list,
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

        active = get_server_status(server)
        if not active:
            flash("Server is Off! Cannot send commands to console!", category="error")
            return redirect(url_for("main.controls", server_id=server_id))

        cmd = [script_path, short_ctrl, send_cmd]

        flash("Sending command to console")
        audit_log_event(current_user.id, f"User '{current_user.username}', sent command '{send_cmd}' to '{server.install_name}'")

        if server.install_type == "docker":
            cmd = docker_cmd_build(server) + cmd

        daemon = Thread(
            target=command_service.run_command,
            args=(cmd, server, server.id, current_app.app_context()),
            daemon=True,
            name="ConsoleCMD",
        )
        daemon.start()
        return redirect(url_for("main.controls", server_id=server_id))

    else:
        if short_ctrl == "st":
            # On start, check if socket_name is null. If so delete the
            # socket file cache for game server before startup. This
            # ensures the status indicators work properly after initial
            # install.
            socket_name = get_tmux_socket_name(server)
            if socket_name == None:
                update_tmux_socket_name_cache(server.id, None, True)

        cmd = [script_path, short_ctrl]

        # Get long_ctrl for matching short_ctrl for audit logging. 
        for control in controls_list:
            if control.short_ctrl == short_ctrl:
                long_ctrl = control.long_ctrl
                break

        audit_log_event(current_user.id, f"User '{current_user.username}', ran '{long_ctrl}' on '{server.install_name}'")

        if server.install_type == "docker":
            cmd = docker_cmd_build(server) + cmd

        daemon = Thread(
            target=command_service.run_command,
            args=(cmd, server, server.id, current_app.app_context()),
            daemon=True,
            name="Command",
        )
        daemon.start()
        return redirect(url_for("main.controls", server_id=server_id))


