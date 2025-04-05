import os
import io
import re
import sys
import json
import time
import signal
import shutil
import getpass
import configparser
import markdown

from threading import Thread
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    url_for,
    redirect,
    Response,
    send_file,
    send_from_directory,
    jsonify,
    current_app,
)

from . import db
from .utils import *
from .models import *
from .proc_info_vessel import ProcInfoVessel

from .processes_global import *

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

api = Blueprint('api', __name__)

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

    current_app.logger.info(log_wrap("installed_servers", installed_servers))
    
    current_app.logger.info(log_wrap("######### SINGLETON TESTING SHARED ITEMS", processes))

    return render_template(
        "home.html",
        user=current_user,
        all_game_servers=installed_servers,
        config_options=config_options,
    )


######### Controls Page #########

@views.route("/controls", methods=["GET"])
@login_required
def controls():
    config_options = read_config("controls")
    current_app.logger.info(log_wrap("config_options", config_options))

    # Collect args from GET request.
    server_id = request.args.get("server_id")
    short_cmd = request.args.get("command")
    console_cmd = request.args.get("cmd")

    # Check if user has permissions to game server for controls route.
    if not user_has_permissions(current_user, "controls", server_id):
        return redirect(url_for("views.home"))

    # Can't load the controls page without a server specified.
    if server_id == None:
        flash("No server specified!", category="error")
        return redirect(url_for("views.home"))

    # Check that the submitted server exists in db.
    server = GameServer.query.filter_by(id=server_id).first()
    # If game server doesn't exist in db, can't load page for it.
    if server == None:
        flash("Invalid game server name!", category="error")
        return redirect(url_for("views.home"))

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

    # If config editor is disabled in the main.conf.
    if not config_options["cfg_editor"]:
        cfg_paths = []
    else:
        cfg_paths = find_cfg_paths(server)
        if cfg_paths == "failed":
            flash("Error reading accepted_cfgs.json!", category="error")
            cfg_paths = []

    # Pull in commands list from commands.json file.
    cmds_list = get_commands(
        server.script_name, config_options["send_cmd"], current_user
    )

    if not cmds_list:
        flash("Error loading commands.json file!", category="error")
        return redirect(url_for("views.home"))

    # Object to hold process info from cmd in daemon thread.
    proc_info = ProcInfoVessel()

    # If this is the first time we're ever seeing the server_id then put it
    # and its associated proc_info in the global servers dictionary.
    if server_id not in get_all_processes():
        add_process(server_id, proc_info)

    proc_info = get_process(server_id)

    script_path = os.path.join(server.install_path, server.script_name)

    # This code block is only triggered in the event the short_cmd param is
    # supplied with the GET request. Aka if a user has clicked one of the
    # control button.
    if short_cmd:
        # Validate short_cmd against contents of commands.json file.
        if not valid_command(
            short_cmd, server.script_name, config_options["send_cmd"], current_user
        ):
            flash("Invalid Command!", category="error")
            return redirect(url_for("views.controls", server_id=server_id))

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
                server_name=server_name,
                server_commands=cmds_list,
                config_options=config_options,
                cfg_paths=cfg_paths,
                console=True,
            )

        elif short_cmd == "sd":
            # Check if send_cmd is enabled in main.conf.
            if not config_options["send_cmd"]:
                flash("Send console command button disabled!", category="error")
                return redirect(url_for("views.controls", server_id=server_id))

            if console_cmd == None:
                flash("No command provided!", category="error")
                return redirect(url_for("views.controls", server_id=server_id))

            active = get_server_status(server)
            if not active:
                flash(
                    "Server is Off! Cannot send commands to console!", category="error"
                )
                return redirect(url_for("views.controls", server_id=server_id))

            cmd = [script_path, short_cmd, console_cmd]

            if should_use_ssh(server):
                pub_key_file = get_ssh_key_file(server.username, server.install_host)
                daemon = Thread(
                    target=run_cmd_ssh,
                    args=(
                        cmd,
                        server.install_host,
                        server.username,
                        pub_key_file,
                        proc_info,
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
                args=(cmd, proc_info, current_app.app_context()),
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
                pub_key_file = get_ssh_key_file(server.username, server.install_host)
                daemon = Thread(
                    target=run_cmd_ssh,
                    args=(
                        cmd,
                        server.install_host,
                        server.username,
                        pub_key_file,
                        proc_info,
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
                args=(cmd, proc_info, current_app.app_context()),
                daemon=True,
                name="Command",
            )
            daemon.start()
            return redirect(url_for("views.controls", server_id=server_id))

    current_app.logger.info(log_wrap("server_id", server_id))
    current_app.logger.info(log_wrap("cmds_list", cmds_list))
    current_app.logger.info(log_wrap("cfg_paths", cfg_paths))

    return render_template(
        "controls.html",
        user=current_user,
        server_id=server_id,
        server_name=server.install_name,
        server_commands=cmds_list,
        config_options=config_options,
        cfg_paths=cfg_paths,
    )


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

    if request.method == "GET":
        server_id = request.args.get("server_id")
        cancel = request.args.get("cancel")
        if server_id != None and cancel == "true":
            server = GameServer.query.filter_by(id=server_id).first()
            if server == None:
                flash("Problem canceling installation! Game server id not found.", category="error")
                return redirect(url_for("views.install"))

            # Check if install thread is still running.
            if server.id not in running_installs:
                flash(
                    "Install for server not currently running!",
                    category="error",
                )
                return redirect(url_for("views.install"))

            proc_info = get_process(server.id)
            current_app.logger.info(log_wrap("proc_info", proc_info))

            if proc_info.pid:
                success = cancel_install(proc_info)
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
        )

    # Note: For install POSTs we need to user server_name cause server not in
    # DB yet so doesn't have an ID.
    if request.method == "POST":
        server_script_name = request.form.get("server_name")
        server_install_name = request.form.get("full_name")

        # Make sure required options are supplied.
        for required_form_item in (server_script_name, server_install_name):
            if required_form_item == None:
                flash("Missing Required Form Field!", category="error")
                return redirect(url_for("views.install"))

            # Check input lengths.
            if len(required_form_item) > 150:
                flash("Form field too long!", category="error")
                return redirect(url_for("views.install"))

        # Validate form submission data against install list in json file.
        if not valid_install_options(server_script_name, server_install_name):
            flash("Invalid Installation Option(s)!", category="error")
            return redirect(url_for("views.install"))

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
            config_options["create_new_user"] = False

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
        if config_options["create_new_user"]:
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

        server_id = (
            GameServer.query.filter_by(install_name=server_install_name).first().id
        )

        # Add new proc_info object for install process and associate with new
        # game server ID.
        proc_info = add_process(server_id, ProcInfoVessel())

        current_app.logger.info(log_wrap("server_id", server_id))
        current_app.logger.info(log_wrap("proc_info", proc_info))

        # Update web user's permissions to give access to new game server post install.
        if current_user.role != "admin":
            user_ident = User.query.filter_by(username=current_user.username).first()
            user_perms = json.loads(user_ident.permissions)
            user_perms["servers"].append(server_id)
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
            args=(cmd, proc_info, current_app.app_context()),
            daemon=True,
            name=f"web_lgsm_install_{server_id}",
        )
        install_daemon.start()

        return render_template(
            "install.html",
            user=current_user,
            servers=install_list,
            config_options=config_options,
            install_name=install_name,
            server_id=server_id,
            running_installs=running_installs,
        )


######### API Update Console #########

@views.route("/api/update-console", methods=["POST"])
@login_required
def update_console():
    global servers

    if not user_has_permissions(current_user, "update-console"):
        resp_dict = {"Error": "Permission denied!"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
        )
        return response

    # Collect var from POST request.
    server_id = request.form.get("server_id")

    # Can't do needful without a server specified.
    if server_id == None:
        resp_dict = {"Error": "Required var: server"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
        )
        return response

    # Check that the submitted server exists in db.
    server = GameServer.query.filter_by(id=server_id).first()
    if server == None:
        resp_dict = {"Error": "Supplied server does not exist!"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
        )
        return response

    tmux_socket = get_tmux_socket_name(server)

    cmd = [
        PATHS["tmux"],
        "-L",
        tmux_socket,
        "capture-pane",
        "-pt",
        server.script_name,
        "-S",
        "-",
        "-E",
        "-",
        "-J",
    ]

    if server.install_type == "docker":
        cmd = docker_cmd_build(server) + cmd

    if server.install_name in servers:
        proc_info = servers[server.install_name]
    else:
        proc_info = ProcInfoVessel()
        servers[server.install_name] = proc_info

    if should_use_ssh(server):
        pub_key_file = get_ssh_key_file(server.username, server.install_host)
        run_cmd_ssh(
            cmd,
            server.install_host,
            server.username,
            pub_key_file,
            proc_info,
            None,
            None,
        )
    else:
        run_cmd_popen(cmd, proc_info)

    if proc_info.exit_status > 0:
        resp_dict = {"Error": "Refresh cmd failed!"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=503, mimetype="application/json"
        )
        return response

    resp_dict = {"Success": "Output updated!"}
    response = Response(
        json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
    )
    return response


######### API Server Statuses #########

@views.route("/api/server-status", methods=["GET"])
@login_required
def get_status():
    # Collect args from GET request.
    server_id = request.args.get("id")

    if server_id == None:
        resp_dict = {"Error": "No id supplied"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
        )
        return response

    server = GameServer.query.get(server_id)
    if server == None:
        resp_dict = {"Error": "Invalid id"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
        )
        return response

    if not user_has_permissions(current_user, "server-statuses", server.install_name):
        resp_dict = {"Error": "Permission Denied!"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
        )
        return response

    server_status = get_server_status(server)
    resp_dict = {"id": server.id, "status": server_status}
    current_app.logger.info(log_wrap("resp_dict", resp_dict))

    response = Response(
        json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
    )
    return response


######### API System Usage #########

@views.route("/api/system-usage", methods=["GET"])
@login_required
def get_stats():
    server_stats = get_server_stats()
    response = Response(
        json.dumps(server_stats, indent=4), status=200, mimetype="application/json"
    )
    return response


######### API CMD Output Page #########

@views.route("/api/cmd-output", methods=["GET"])
@login_required
def no_output():
    global servers

    # Collect args from GET request.
    server_id = request.args.get("server_id")

    # Can't load the controls page without a server specified.
    if server_id == None:
        resp_dict = {"error": "eer can't load page n'@"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
        )
        return response

    # Can't do anything if we don't have proc info vessel stored.
    if server_id not in get_all_processes():
        resp_dict = {"error": "eer never heard of em"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
        )
        return response

    if not user_has_permissions(current_user, "cmd-output", server_id):
        resp_dict = {"Error": "Permission Denied!"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
        )
        return response

    output = get_process(server_id)

    # Returns json for used by ajax code on /controls route.
    response = Response(output.toJSON(), status=200, mimetype="application/json")
    return response


######### Settings Page #########

@views.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    # Check if user has permissions to settings route.
    if not user_has_permissions(current_user, "settings"):
        return redirect(url_for("views.home"))

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
        return render_template(
            "settings.html",
            user=current_user,
            system_user=USER,
            config_options=config_options,
        )

    # TODO v1.9: Retrieve form options via separate function like read_config()
    # (maybe read_form()) to cleanup the mess that is the block of text below.
    text_color_pref = request.form.get("text_color")
    user_del_pref = request.form.get("delete_user")
    file_pref = request.form.get("delete_files")
    clear_output_pref = request.form.get("clear_output_on_reload")
    height_pref = request.form.get("terminal_height")
    update_weblgsm = request.form.get("update_weblgsm")
    graphs_primary_pref = request.form.get("graphs_primary")
    graphs_secondary_pref = request.form.get("graphs_secondary")
    show_stats_pref = request.form.get("show_stats")
    purge_tmux_cache = request.form.get("purge_tmux_cache")
    install_new_user_pref = request.form.get("install_new_user")
    newline_ending_pref = request.form.get("newline_ending")
    show_stderr_pref = request.form.get("show_stderr")

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

    # Text color settings.
    def valid_color(color):
        # Validate color code with regular expression.
        if re.search("^#(?:[0-9a-fA-F]{1,2}){3}$", color):
            return True

        return False

    if text_color_pref:
        if not valid_color(text_color_pref):
            flash("Invalid text color!", category="error")
            return redirect(url_for("views.settings"))
        config["aesthetic"]["text_color"] = text_color_pref

    if graphs_primary_pref:
        if not valid_color(graphs_primary_pref):
            flash("Invalid primary color!", category="error")
            return redirect(url_for("views.settings"))
        config["aesthetic"]["graphs_primary"] = graphs_primary_pref

    if graphs_secondary_pref:
        if not valid_color(graphs_secondary_pref):
            flash("Invalid secondary color!", category="error")
            return redirect(url_for("views.settings"))
        config["aesthetic"]["graphs_secondary"] = graphs_secondary_pref

    # Default to no, if checkbox is unchecked.
    config["aesthetic"]["show_stats"] = "no"
    if show_stats_pref == "true":
        config["aesthetic"]["show_stats"] = "yes"

    # Set default text area height setting.
    config["aesthetic"]["terminal_height"] = config_options["terminal_height"]
    if height_pref:
        # Validate terminal height is int.
        try:
            height_pref = int(height_pref)
        except ValueError:
            flash("Invalid Terminal Height!", category="error")
            return redirect(url_for("views.settings"))

        # Check if height pref is invalid range.
        if height_pref > 100 or height_pref < 5:
            flash("Invalid Terminal Height!", category="error")
            return redirect(url_for("views.settings"))

        # Have to cast back to string to save in config.
        config["aesthetic"]["terminal_height"] = str(height_pref)

    with open(config_file, "w") as configfile:
        config.write(configfile)

    # Update's the weblgsm.
    if update_weblgsm:
        status = update_self()
        flash("Settings Updated!")
        if "Error:" in status:
            flash(status, category="error")
            return redirect(url_for("views.settings"))

        flash(status)

        cmd = ["./web-lgsm.py", "--restart"]
        restart_daemon = Thread(
            target=run_cmd_popen,
            args=(cmd, ProcInfoVessel(), current_app.app_context()),
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
    changelog_html =  markdown.markdown(changelog_md)

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

    # Set default status_code.
    status_code = 200

    if request.method == "POST":
        server = GameServer()
        server.install_finished = True  # All server adds are auto marked finished.

        install_name = request.form.get("install_name")
        install_path = request.form.get("install_path")
        script_name = request.form.get("script_name")
        username = request.form.get("username")
        install_type = request.form.get("install_type")
        install_host = request.form.get("install_host")

        ## Validation Logic.
        # Check all required args are submitted.
        for required_form_item in (
            install_name,
            install_path,
            script_name,
            install_type,
        ):
            if required_form_item == None or required_form_item == "":
                flash("Missing required form field(s)!", category="error")
                return render_template("add.html", user=current_user), 400

            # Check input lengths.
            if len(required_form_item) > 150:
                flash("Form field too long!", category="error")
                return render_template("add.html", user=current_user), 400

        if not valid_script_name(script_name):
            flash("Invalid game server script file name!", category="error")
            status_code = 400
            return render_template("add.html", user=current_user), status_code

        # Set default user if none provided.
        if username == None or username == "":
            username = USER

        if len(username) > 150:
            flash("Form field too long!", category="error")
            return render_template("add.html", user=current_user), 400

        # Try to prevent arbitrary bad input.
        for input_item in (install_name, install_path, script_name, username):
            if contains_bad_chars(input_item):
                flash("Illegal Character Entered!", category="error")
                flash(
                    r"""Bad Chars: $ ' " \ # = [ ] ! < > | ; { } ( ) * , ? ~ &""",
                    category="error",
                )
                status_code = 400
                return render_template("add.html", user=current_user), status_code

        # Make install name unix friendly for dir creation.
        install_name = install_name.replace(" ", "_")
        install_name = install_name.replace(".", "_")
        install_name = install_name.replace(":", "")

        # Validate install_type.
        if not valid_install_type(install_type):
            flash("Invalid install type!", category="error")
            return render_template("add.html", user=current_user), 400

        ## Log & set GameServer obj vars after most of the validation is done.
        current_app.logger.info(log_wrap("install_name", install_name))
        current_app.logger.info(log_wrap("install_path", install_path))
        current_app.logger.info(log_wrap("script_name", script_name))
        current_app.logger.info(log_wrap("username", username))
        current_app.logger.info(log_wrap("install_type", install_type))

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

            # Returns None if not valid username.
            if get_uid(username) == None:
                flash("User not found on system!", category="error")
                status_code = 400
                return render_template("add.html", user=current_user), status_code

        install_exists = GameServer.query.filter_by(install_name=install_name).first()

        if install_exists:
            flash("An installation by that name already exits.", category="error")
            status_code = 400
            return render_template("add.html", user=current_user), status_code

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

        flash("Game server added!")
        return redirect(url_for("views.home"))

    return render_template("add.html", user=current_user), status_code


######### Delete Route #########

@views.route("/delete", methods=["GET", "POST"])
@login_required
def delete():

    # TODO v1.9: I'm thinking of adding an additional perms check here just to
    # see if user can access route. Will still also keep server specific check
    # below. Idk still have to think about it a bit.

    config_options = read_config("delete")
    current_app.logger.info(log_wrap("config_options", config_options))

    # NOTE: For everyone's safety, if config options are incongruous, default
    # to safer keep user, keep files option. (ie. If delete_user is True and
    # remove_files is False, default to keep user. Cannot delete the user and
    # keep their files. That is technically possible in Linux. However, to make
    # things easier on me and hide some unnecessary complexity, my app does not
    # allow it and will default to keeping users & files in that case.)
    if config_options["delete_user"] and not config_options["remove_files"]:
        flash(
            "Incongruous config options detected. Defaulting to safer keep user, keep files option",
            category="error",
        )
        config_options["delete_user"] = False

    def del_wrap(server_id):
        """Wraps up delete logic used below"""
        # Check if user has permissions to delete route & server.
        if not user_has_permissions(current_user, "delete", server_id):
            return redirect(url_for("views.home"))

        current_app.logger.info(log_wrap(f"{current_user} deleting ID: ", server_id))

        server = GameServer.query.filter_by(id=server_id).first()
        if server == None:
            flash("No such server found!", category="error")
            return redirect(url_for("views.home"))

        current_app.logger.info(server)

        # Drop any saved proc_info objects.
        remove_process(server_id)

        # Log to ensure process was dropped.
        current_app.logger.info(log_wrap("All processes", get_all_processes()))

        if not delete_server(
            server, config_options["remove_files"], config_options["delete_user"]
        ):
            flash(
                f"Something's gone wrong deleting server, {server_name}",
                category="error",
            )

        # We don't want to keep deleted servers in the cache.
        update_tmux_socket_name_cache(server_id, None, True)

    # Delete via POST is for multiple deletions.
    # Post submissions come from delete toggles on home page.
    if request.method == "POST":
        for tag, server_id in request.form.items():
            del_wrap(server_id)
    else:
        server_name = request.args.get("server")
        if server_name == None:
            flash("Missing Required Args!", category="error")
            return redirect(url_for("views.home"))

        del_wrap(server_name)

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

    # Collect args from POST request.
    server_id = request.form.get("server_id")
    cfg_path = request.form.get("cfg_path")
    new_file_contents = request.form.get("file_contents")
    download = request.form.get("download")

    # Can't load the edit page without a server specified.
    if server_name == None or server_name == "":
        flash("No server specified!", category="error")
        return redirect(url_for("views.home"))

    # Can't load the edit page without a cfg specified.
    if cfg_path == None or cfg_path == "":
        flash("No config file specified!", category="error")
        return redirect(url_for("views.home"))

    # Check that the submitted server exists in db.
    server = GameServer.query.filter_by(install_name=server_name).first()
    # If game server doesn't exist in db, can't load page for it.
    if server == None:
        flash("Invalid game server name!", category="error")
        return redirect(url_for("views.home"))

    # Try to pull script's basename from supplied cfg_path.
    try:
        cfg_file = os.path.basename(cfg_path)
    except:
        flash("Error getting config file basename!", category="error")
        return redirect(url_for("views.home"))

    # Validate cfg_file name is in list of accepted cfgs.
    if not valid_cfg_name(cfg_file):
        flash("Invalid config file name!", category="error")
        return redirect(url_for("views.home"))

    if should_use_ssh(server):
        # If new contents are supplied via POST, write them to file over ssh.
        if new_file_contents:
            written = write_file_over_ssh(
                server, cfg_path, new_file_contents.replace("\r", "")
            )
            if written:
                flash("Cfg file updated!", category="success")
            else:
                flash("Error writing to cfg file!", category="error")
                return redirect(url_for("views.home"))

        # Read in file contents over ssh.
        file_contents = read_file_over_ssh(server, cfg_path)
        if file_contents == None:
            flash("Problem reading cfg file!", category="error")
            return redirect(url_for("views.home"))

        # If is download request.
        if download == "yes":
            file_like_thingy = io.BytesIO(file_contents.encode("utf-8"))
            return send_file(
                file_like_thingy,
                as_attachment=True,
                download_name=cfg_file,
                mimetype="text/plain",
            )
    else:
        # Check that file exists before allowing writes to it. Aka don't allow
        # arbitrary file creation. Even though the above should block creating
        # files with arbitrary names, we still don't want to allow arbitrary file
        # creation anywhere on the file system the app has write perms to.
        if not os.path.isfile(cfg_path):
            flash("No such file!", category="error")
            return redirect(url_for("views.home"))

        # If new_file_contents supplied in post request, write the new file
        # contents to the cfg file.
        if new_file_contents:
            try:
                with open(cfg_path, "w") as f:
                    f.write(new_file_contents.replace("\r", ""))
                flash("Cfg file updated!", category="success")
            except:
                flash("Error writing to cfg file!", category="error")

        # Read in file contents from cfg file.
        file_contents = ""
        # Try except in case problem with file.
        try:
            with open(cfg_path) as f:
                file_contents = f.read()
        except:
            flash("Error reading config!", category="error")
            return redirect(url_for("views.home"))

        # If is download request.
        if download == "yes":
            basedir, basename = os.path.split(cfg_path)
            return send_from_directory(basedir, basename, as_attachment=True)

    return render_template(
        "edit.html",
        user=current_user,
        server_name=server_name,
        cfg_file=cfg_path,
        file_contents=file_contents,
        cfg_file_name=cfg_file,
    )
