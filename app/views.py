import os
import json
import yaml
import getpass
import configparser
import markdown

from threading import Thread
from flask_login import login_required, current_user
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    url_for,
    redirect,
    current_app,
)

from . import db
from .utils import *
from .models import *
from .proc_info_vessel import ProcInfoVessel
from .processes_global import *
from .forms import *
from . import cache

# Constants.
CWD = os.getcwd()
USER = getpass.getuser()
VENV = "/opt/web-lgsm/"
ANSIBLE_CONNECTOR = "/usr/local/bin/ansible_connector.py"
PATHS = {
    "docker": "/usr/bin/docker",
    "sudo": "/usr/bin/sudo",
    "tmux": "/usr/bin/tmux",
}

# Initialize view blueprint.
views = Blueprint("views", __name__)


######### Home Page #########

@views.route("/", methods=["GET"])
@views.route("/home", methods=["GET"])
@login_required
def home():
    config_options = read_config("home")
    current_app.logger.info(log_wrap("config_options", config_options))

    current_app.logger.info(str(type(current_user)))
    current_app.logger.info(log_wrap("current_user.username", current_user.username))
    current_app.logger.info(log_wrap("current_user.role", current_user.role))
    current_app.logger.info(
        log_wrap("current_user.permissions", current_user.permissions)
    )

    installed_servers = GameServer.query.all()
    for server in installed_servers:
        current_app.logger.info(server.id)

    current_app.logger.debug(log_wrap("installed_servers", installed_servers))
    for proc_id, proc in get_all_processes().items():
        current_app.logger.debug(log_wrap(proc_id, proc))

    return render_template(
        "home.html",
        user=current_user,
        all_game_servers=installed_servers,
        config_options=config_options,
    )


######### Controls Page #########

@views.route("/controls", methods=["GET", "POST"])
@login_required
def controls():
    config_options = read_config("controls")
    current_app.logger.info(log_wrap("config_options", config_options))

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
                return redirect(url_for("views.home"))

            return redirect(url_for("views.controls", server_id=server.id))

        # Checking id is valid.
        id_form = ValidateID(request.args)
        if not id_form.validate():
            validation_errors(id_form)
            return redirect(url_for("views.home"))

        server_id = request.args.get("server_id")
        server = GameServer.query.filter_by(id=server_id).first()
        current_app.logger.info(log_wrap("server_id", server_id))

        # Check if user has permissions to game server for controls route.
        if not user_has_permissions(current_user, "controls", server_id):
            return redirect(url_for("views.home"))

        # Pull in commands list from commands.json file.
        cmds_list = get_commands(
            server.script_name, config_options["send_cmd"], current_user
        )

        if should_use_ssh(server):
            if not is_ssh_accessible(server.install_host):
                if server.install_type == "remote":
                    flash("Unable to access remote server over ssh!", category="error")
                    return redirect(url_for("views.home"))
                else:
                    flash("Unable to access local install over ssh!", category="error")
                    return redirect(url_for("views.home"))

        elif server.install_type == "local" and not os.path.isdir(server.install_path):
            flash("No game server installation directory found!", category="error")
            return redirect(url_for("views.home"))

        # Cfg editor buttons stuff.
        cache_key = f"cfg_paths_{server_id}"
        cfg_paths = cache.get(cache_key)

        if not config_options["cfg_editor"]:
            cfg_paths = []

        elif cfg_paths is None:  # Not in cache.
            current_app.logger.info("Getting cfg_paths")
            cfg_paths = find_cfg_paths(server)

            if cfg_paths == "failed":
                flash("Error reading accepted_cfgs.json!", category="error")
                cfg_paths = []

            cache.set(cache_key, cfg_paths, timeout=1800)

        current_app.logger.info(log_wrap("cfg_paths", cfg_paths))

        return render_template(
            "controls.html",
            user=current_user,
            server_id=server_id,
            server_name=server.install_name,
            server_commands=cmds_list,
            config_options=config_options,
            cfg_paths=cfg_paths,
            select_cfg_form=select_cfg_form,
            controls_form=controls_form,
            send_cmd_form=send_cmd_form,
        )

    # Handle POST requests.
    if controls_form.ctrl_form.data:
        if not controls_form.validate_on_submit():
            validation_errors(controls_form)
            return redirect(url_for("views.home"))

        server_id = controls_form.server_id.data
        short_cmd = controls_form.command.data

    elif send_cmd_form.send_form.data:
        if not send_cmd_form.validate_on_submit():
            validation_errors(send_cmd_form)
            return redirect(url_for("views.home"))

        server_id = send_cmd_form.server_id.data
        short_cmd = send_cmd_form.command.data
        send_cmd = send_cmd_form.send_cmd.data

    else:
        flash("Invalid form submission!", category="error")
        return redirect(url_for("views.controls", server_id=server_id))

    server = GameServer.query.filter_by(id=server_id).first()
    current_app.logger.info(log_wrap("server_id", server_id))

    # TODO: Eventually find a way to move this into ServerControlForm class
    # validation. Problem is right now, not sure how to validate server id
    # first, then get server in order to run this validation. So this works for
    # rn.
    # Validate short_cmd against contents of commands.json file.
    if not valid_command(
        short_cmd, server.script_name, config_options["send_cmd"], current_user
    ):
        flash("Invalid Command!", category="error")
        return redirect(url_for("views.controls", server_id=server_id))

    # Check if user has permissions to game server for controls route.
    if not user_has_permissions(current_user, "controls", server_id):
        return redirect(url_for("views.home"))

    # If cfg editor is disabled in the main.conf.
    if not config_options["cfg_editor"]:
        cfg_paths = []
    else:
        current_app.logger.info("Getting cfg_paths")
        cfg_paths = find_cfg_paths(server)
        if cfg_paths == "failed":
            flash("Error reading accepted_cfgs.json!", category="error")
            cfg_paths = []

    current_app.logger.info(log_wrap("cfg_paths", cfg_paths))

    # Pull in commands list from commands.json file.
    cmds_list = get_commands(
        server.script_name, config_options["send_cmd"], current_user
    )

    if not cmds_list:
        flash("Error loading commands.json file!", category="error")
        return redirect(url_for("views.home"))

    script_path = os.path.join(server.install_path, server.script_name)

    # Console option, use tmux capture-pane to get output.
    if short_cmd == "c":
        active = get_server_status(server)
        if not active:
            flash("Server is Off! No Console Output!", category="error")
            return redirect(url_for("views.controls", server_id=server_id))

        # Console mode is trigger in JS, set off by console=True. Nothing
        # for backend console happens here. See /api/update-console route!
        return render_template(
            "controls.html",
            user=current_user,
            server_id=server_id,
            server_name=server.install_name,
            server_commands=cmds_list,
            config_options=config_options,
            cfg_paths=cfg_paths,
            select_cfg_form=select_cfg_form,
            controls_form=controls_form,
            send_cmd_form=send_cmd_form,
            console=True,
        )

    elif short_cmd == "sd":
        # Check if send_cmd is enabled in main.conf.
        if not config_options["send_cmd"]:
            flash("Send console command button disabled!", category="error")
            return redirect(url_for("views.controls", server_id=server_id))

        active = get_server_status(server)
        if not active:
            flash("Server is Off! Cannot send commands to console!", category="error")
            return redirect(url_for("views.controls", server_id=server_id))

        cmd = [script_path, short_cmd, send_cmd]

        flash("Sending command to console")
        if should_use_ssh(server):
            daemon = Thread(
                target=run_cmd_ssh,
                args=(
                    cmd,
                    server,
                    current_app.app_context(),
                    None,
                ),
                daemon=True,
                name="send",
            )
            daemon.start()
            return redirect(url_for("views.controls", server_id=server_id))

        if server.install_type == "docker":
            cmd = docker_cmd_build(server) + cmd

        daemon = Thread(
            target=run_cmd_popen,
            args=(cmd, server_id, current_app.app_context()),
            daemon=True,
            name="ConsoleCMD",
        )
        daemon.start()
        return redirect(url_for("views.controls", server_id=server_id))

    else:
        if short_cmd == "st":
            # On start, check if socket_name is null. If so delete the
            # socket file cache for game server before startup. This
            # ensures the status indicators work properly after initial
            # install.
            socket_name = get_tmux_socket_name(server)
            if socket_name == None:
                update_tmux_socket_name_cache(server.id, None, True)

        cmd = [script_path, short_cmd]

        if should_use_ssh(server):
            daemon = Thread(
                target=run_cmd_ssh,
                args=(
                    cmd,
                    server,
                    current_app.app_context(),
                ),
                daemon=True,
                name="Command",
            )
            daemon.start()
            return redirect(url_for("views.controls", server_id=server_id))

        if server.install_type == "docker":
            cmd = docker_cmd_build(server) + cmd

        daemon = Thread(
            target=run_cmd_popen,
            args=(cmd, server_id, current_app.app_context()),
            daemon=True,
            name="Command",
        )
        daemon.start()
        return redirect(url_for("views.controls", server_id=server_id))


######### Install Page #########

@views.route("/install", methods=["GET", "POST"])
@login_required
def install():
    # Check if user has permissions to install route.
    if not user_has_permissions(current_user, "install"):
        return redirect(url_for("views.home"))

    config_options = read_config("install")
    current_app.logger.info(log_wrap("config_options", config_options))

    # Pull in install server list from game_servers.json file.
    install_list = get_servers()
    if not install_list:
        flash("Error loading game_servers.json file!", category="error")
        return redirect(url_for("views.home"))

    # Initialize blank install_name, used for update-text-area.js.
    install_name = ""

    # Check for / install the main linuxgsm.sh script.
    lgsmsh = "linuxgsm.sh"
    check_and_get_lgsmsh(f"scripts/{lgsmsh}")

    # Check if any installs are currently running.
    running_installs = get_running_installs()

    form = InstallForm()

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
                return redirect(url_for("views.install"))

            # Check if install thread is still running.
            if server.id not in running_installs:
                flash(
                    "Install for server not currently running!",
                    category="error",
                )
                return redirect(url_for("views.install"))

            # Log proc info so can see what's going on.
            proc_info = get_process(server.id)
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
            servers=install_list,
            install_name=install_name,
            server_id=server_id,
            config_options=config_options,
            running_installs=running_installs,
            form=form,
        )

    # Handle POSTs

    # Handle Invalid form submissions.
    if not form.validate_on_submit():
        validation_errors(form)
        return redirect(url_for("views.install"))

    # NOTE: For install POSTs we need to user server_name cause server not in
    # DB yet so doesn't have an ID.
    server_script_name = form.script_name.data
    server_install_name = form.full_name.data

    # Make server_install_name a unix friendly directory name.
    server_install_name = server_install_name.replace(" ", "_")
    server_install_name = server_install_name.replace(":", "")

    # Used to pass install_name to frontend js.
    install_name = server_install_name

    install_exists = GameServer.query.filter_by(
        install_name=server_install_name
    ).first()

    if install_exists:
        flash("An installation by that name already exits.", category="error")
        return redirect(url_for("views.install"))

    # If running in a container do not allow install new user! For design
    # reasons, to keep things simple. Inside of a container installs are
    # going to be same user only.
    if "CONTAINER" in os.environ:
        config_options["install_create_new_user"] = False

    server = GameServer()
    server.install_name = server_install_name
    server.install_path = os.path.join(CWD, f"GameServers/{server_install_name}")
    server.script_name = server_script_name
    server.username = USER
    server.is_container = False
    server.install_type = "local"
    server.install_host = "127.0.0.1"
    server.install_finished = False
    server.keyfile_path = ""

    # If install_create_new_user config parameter is true then create a new
    # user for the new game server and set install path to the path in that
    # new users home directory.
    if config_options["install_create_new_user"]:
        server.username = server_script_name
        server.install_path = (
            f"/home/{server_script_name}/GameServers/{server_install_name}"
        )

        # Add keyfile path for server to DB.
        keyfile = get_ssh_key_file(server.username, server.install_host)
        server.keyfile_path = keyfile

    current_app.logger.info(log_wrap("server", server))

    # Add the install to the database.
    db.session.add(server)
    db.session.commit()

    server_id = GameServer.query.filter_by(install_name=server_install_name).first().id

    # Add new proc_info object for install process and associate with new
    # game server ID.
    #    proc_info = add_process(server_id, ProcInfoVessel())

    current_app.logger.info(log_wrap("server_id", server_id))
    #    current_app.logger.info(log_wrap("proc_info", proc_info))

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
        ANSIBLE_CONNECTOR,
        "--install",
        str(server_id),
    ]

    current_app.logger.info(log_wrap("cmd", cmd))
    current_app.logger.info(log_wrap("all processes", get_all_processes()))

    install_daemon = Thread(
        target=run_cmd_popen,
        args=(cmd, server_id, current_app.app_context()),
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

    return render_template(
        "install.html",
        user=current_user,
        servers=install_list,
        config_options=config_options,
        install_name=install_name,
        server_id=server_id,
        running_installs=running_installs,
        form=form,
    )


######### Settings Page #########

@views.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    # Check if user has permissions to settings route.
    if not user_has_permissions(current_user, "settings"):
        return redirect(url_for("views.home"))

    # Create SettingsForm.
    form = SettingsForm()

    # Since settings also writes to config, open config parse here too.
    config = configparser.ConfigParser()
    config_file = "main.conf"
    config_local = "main.conf.local"  # Local config override.
    if os.path.isfile(config_local) and os.access(config_local, os.R_OK):
        config_file = config_local
    current_app.logger.info(log_wrap("config_file", config_file))
    config.read(config_file)

    # But still pull all settings from read_config() wrapper.
    config_options = read_config("settings")
    current_app.logger.info(log_wrap("config_options", config_options))

    if request.method == "GET":
        # Set form defaults.
        # NOTE: This logic for setting defaults could be moved into the
        # SettingsForm class, still thinking abt if I want to do that or not...
        form.text_color.default = config_options["text_color"]
        form.graphs_primary.default = config_options["graphs_primary"]
        form.graphs_secondary.default = config_options["graphs_secondary"]
        form.terminal_height.default = config_options["terminal_height"]
        form.delete_user.default = str(config_options["delete_user"]).lower()
        form.remove_files.default = str(config_options["remove_files"]).lower()
        form.install_new_user.default = str(
            config_options["install_create_new_user"]
        ).lower()
        form.newline_ending.default = str(config_options["end_in_newlines"]).lower()
        form.show_stderr.default = str(config_options["show_stderr"]).lower()
        form.clear_output_on_reload.default = str(
            config_options["clear_output_on_reload"]
        ).lower()
        # BooleanFields handle setting default differently from RadioFields.
        if config_options["show_stats"]:
            form.show_stats.default = "true"
        form.process()  # Required to apply form changes.

        return render_template(
            "settings.html",
            user=current_user,
            system_user=USER,
            config_options=config_options,
            form=form,
        )

    # Handle Invalid form submissions.
    if not form.validate_on_submit():
        validation_errors(form)
        return redirect(url_for("views.settings"))

    # TODO v1.9: Retrieve form options via separate function like read_config()
    # (maybe read_form()) to cleanup the mess that is the block of text below.
    text_color_pref = str(form.text_color.data).lower()
    user_del_pref = str(form.delete_user.data).lower()
    file_pref = str(form.remove_files.data).lower()
    clear_output_pref = str(form.clear_output_on_reload.data).lower()
    height_pref = str(form.terminal_height.data).lower()
    update_weblgsm = str(form.update_weblgsm.data).lower()
    graphs_primary_pref = str(form.graphs_primary.data).lower()
    graphs_secondary_pref = str(form.graphs_secondary.data).lower()
    show_stats_pref = str(form.show_stats.data).lower()
    purge_tmux_cache = str(form.purge_tmux_cache.data).lower()
    install_new_user_pref = str(form.install_new_user.data).lower()
    newline_ending_pref = str(form.newline_ending.data).lower()
    show_stderr_pref = str(form.show_stderr.data).lower()

    # Debug messages.
    current_app.logger.info(log_wrap("text_color_pref", text_color_pref))
    current_app.logger.info(log_wrap("delete_user_pref", user_del_pref))
    current_app.logger.info(log_wrap("file_pref", file_pref))
    current_app.logger.info(log_wrap("clear_output_pref", clear_output_pref))
    current_app.logger.info(log_wrap("height_pref", height_pref))
    current_app.logger.info(log_wrap("update_weblgsm", update_weblgsm))
    current_app.logger.info(log_wrap("graphs_primary_pref", graphs_primary_pref))
    current_app.logger.info(log_wrap("graphs_secondary_pref", graphs_secondary_pref))
    current_app.logger.info(log_wrap("show_stats_pref", show_stats_pref))
    current_app.logger.info(log_wrap("purge_tmux_cache", purge_tmux_cache))
    current_app.logger.info(log_wrap("install_new_user_pref", install_new_user_pref))
    current_app.logger.info(log_wrap("newline_ending_pref", newline_ending_pref))
    current_app.logger.info(log_wrap("show_stderr_pref", show_stderr_pref))

    if purge_tmux_cache != None:
        purge_tmux_socket_cache()

    # Set Remove user setting.
    config["settings"]["delete_user"] = "yes"
    if user_del_pref == "false":
        config["settings"]["delete_user"] = "no"

    # Set Remove files setting.
    config["settings"]["remove_files"] = "yes"
    if file_pref == "false":
        config["settings"]["remove_files"] = "no"

    config["settings"]["clear_output_on_reload"] = "yes"
    if clear_output_pref == "false":
        config["settings"]["clear_output_on_reload"] = "no"

    # Set New user install setting.
    config["settings"]["install_create_new_user"] = "yes"
    if install_new_user_pref == "false":
        config["settings"]["install_create_new_user"] = "no"

    # Newline ending settings.
    config["settings"]["end_in_newlines"] = "yes"
    if newline_ending_pref == "false":
        config["settings"]["end_in_newlines"] = "no"

    # Show stderr setting.
    config["settings"]["show_stderr"] = "yes"
    if show_stderr_pref == "false":
        config["settings"]["show_stderr"] = "no"

    if text_color_pref:
        config["aesthetic"]["text_color"] = text_color_pref

    if graphs_primary_pref:
        config["aesthetic"]["graphs_primary"] = graphs_primary_pref

    if graphs_secondary_pref:
        config["aesthetic"]["graphs_secondary"] = graphs_secondary_pref

    # Default to no, if checkbox is unchecked.
    config["aesthetic"]["show_stats"] = "no"
    if show_stats_pref == "true":
        config["aesthetic"]["show_stats"] = "yes"

    # Set default text area height setting.
    config["aesthetic"]["terminal_height"] = config_options["terminal_height"]
    if height_pref:
        # Have to cast to string to save in config.
        config["aesthetic"]["terminal_height"] = str(height_pref)

    with open(config_file, "w") as configfile:
        config.write(configfile)

    # Update's the weblgsm.
    if update_weblgsm == "true":
        status = update_self()
        if "Error:" in status:
            flash(status, category="error")
            return redirect(url_for("views.settings"))

        flash(status)

        cmd = ["./web-lgsm.py", "--restart"]
        restart_daemon = Thread(
            target=run_cmd_popen,
            args=(cmd, str(uuid.uuid4()), current_app.app_context()),
            daemon=True,
            name="restart",
        )
        restart_daemon.start()
        return redirect(url_for("views.settings"))

    flash("Settings Updated!")
    return redirect(url_for("views.settings"))


######### About Page #########

@views.route("/about", methods=["GET"])
@login_required
def about():
    config_options = read_config("about")
    current_app.logger.info(log_wrap("config_options", config_options))

    return render_template(
        "about.html", user=current_user, config_options=config_options
    )


######### Changelog Page #########

@views.route("/changelog", methods=["GET"])
@login_required
def changelog():
    changelog_md = read_changelog()
    changelog_html = markdown.markdown(changelog_md)

    return render_template(
        "changelog.html", user=current_user, changelog_html=changelog_html
    )


######### Add Page #########

@views.route("/add", methods=["GET", "POST"])
@login_required
def add():
    # Check if user has permissions to add route.
    if not user_has_permissions(current_user, "add"):
        return redirect(url_for("views.home"))

    status_code = 200
    form = AddForm()

    if request.method == "GET":
        return render_template("add.html", user=current_user, form=form), status_code

    # Handle Invalid form submissions.
    if not form.validate_on_submit():
        validation_errors(form)
        return redirect(url_for("views.add"))

    # Process form submissions.
    install_name = form.install_name.data
    install_path = form.install_path.data
    script_name = form.script_name.data
    username = form.username.data
    install_type = form.install_type.data
    install_host = form.install_host.data

    server = GameServer()
    server.install_finished = True  # All server adds are auto marked finished.

    # Set default user if none provided.
    if username == None or username == "":
        username = USER

    # Make install name unix friendly for dir creation.
    install_name = install_name.replace(" ", "_")
    install_name = install_name.replace(".", "_")
    install_name = install_name.replace(":", "")

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
            return render_template("add.html", user=current_user), 400

        if not is_ssh_accessible(install_host):
            flash("Server does not appear to be SSH accessible!", category="error")
            return render_template("add.html", user=current_user), 400

        server.install_type = "remote"
        server.install_host = install_host

    if install_type == "local":
        server.install_type = "local"
        server.install_host = "127.0.0.1"

        if get_uid(username) == None:
            flash("User not found on system!", category="error")
            return redirect(url_for("views.add"))

    install_exists = GameServer.query.filter_by(install_name=install_name).first()

    if install_exists:
        flash("An installation by that name already exits.", category="error")
        return redirect(url_for("views.add"))

    if install_type == "docker":
        flash(
            f"For docker installs be sure to add the following sudoers rule to /etc/sudoers.d/{USER}-docker"
        )
        flash(
            f"{USER} ALL=(root) NOPASSWD: /usr/bin/docker exec --user {server.username} {server.script_name} *"
        )

    if should_use_ssh(server):
        keyfile = get_ssh_key_file(username, server.install_host)
        if keyfile == None:
            flash(f"Problem generating new ssh keys!", category="error")
            return redirect(url_for("views.add"))

        flash(
            f"Add this public key: {keyfile}.pub to the remote server's ~{username}/.ssh/authorized_keys file!"
        )

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
    return redirect(url_for("views.home"))


######### Edit Route #########

@views.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    # NOTE: The abbreviation cfg will be used to refer to any lgsm game server
    # specific config files. Whereas, the word config will be used to refer to
    # any web-lgsm config info.

    config_options = read_config("edit")
    current_app.logger.info(log_wrap("config_options", config_options))

    if not config_options["cfg_editor"]:
        flash("Config Editor Disabled", category="error")
        return redirect(url_for("views.home"))

    upload_form = UploadTextForm()
    download_form = DownloadCfgForm()

    if request.method == "GET":
        current_app.logger.debug(request.args.keys())
        if "download_submit" in request.args.keys():
            download_form = DownloadCfgForm(request.args)
            if not download_form.validate():
                validation_errors(download_form)
                return redirect(url_for("views.home"))

            server_id = download_form.server_id.data
            cfg_path = download_form.cfg_path.data
            server = GameServer.query.filter_by(id=server_id).first()

            return download_cfg(server, cfg_path)

        # Convert raw get args into select_form args.
        select_form = SelectCfgForm(request.args)
        if not select_form.validate():
            validation_errors(select_form)
            return redirect(url_for("views.home"))

        server_id = select_form.server_id.data
        cfg_path = select_form.cfg_path.data
        server = GameServer.query.filter_by(id=server_id).first()

        current_app.logger.info(log_wrap("server_id", server_id))
        current_app.logger.info(log_wrap("cfg_path", cfg_path))
        current_app.logger.info(log_wrap("server", server))

        file_contents = read_cfg_file(server, cfg_path)

        if file_contents == None:
            flash("Error reading file!", category="error")
            return redirect(url_for("views.home"))

        return render_template(
            "edit.html",
            user=current_user,
            server_id=server.id,
            cfg_file=cfg_path,
            file_contents=file_contents,
            download_form=download_form,
            upload_form=upload_form,
        )

    # Handle POSTs.

    # Handle Invalid form submissions.
    if not upload_form.validate_on_submit():
        validation_errors(upload_form)
        return redirect(url_for("views.home"))

    # Process form submissions.
    server_id = upload_form.server_id.data
    cfg_path = upload_form.cfg_path.data
    new_file_contents = upload_form.file_contents.data
    server = GameServer.query.filter_by(id=server_id).first()

    if write_cfg(server, cfg_path, new_file_contents):
        flash("Cfg file updated!", category="success")
    else:
        flash("Error writing to cfg file!", category="error")

    return redirect(url_for("views.edit", server_id=server_id, cfg_path=cfg_path))


######### Swagger API Docs #########

def load_spec():
    spec_path = os.path.join(os.path.dirname(__file__), "specs", "api_spec.yaml")
    with open(spec_path, "r") as f:
        spec = yaml.safe_load(f)

    base_url = request.host_url.rstrip("/")
    api_url = f"{base_url}/api"

    spec["servers"] = [{"url": api_url, "description": "Current host"}]

    return spec


@views.route("/api/spec")
@login_required
def get_spec():
    return load_spec()

