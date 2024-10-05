import os
import re
import sys
import json
import time
import signal
import shutil
import getpass
import configparser

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
    send_from_directory,
    jsonify,
    current_app
)

from . import db
from .utils import *
from .models import *
from .proc_info_vessel import ProcInfoVessel

# Constants.
CWD = os.getcwd()
USER = getpass.getuser()
ANSIBLE_CONNECTOR = os.path.join(CWD, "playbooks/sudo_ansible_connector.py")
# Bootstrap spinner colors.
SPINNER_COLORS = [
    "primary",
    "secondary",
    "success",
    "danger",
    "warning",
    "info",
    "light",
]

# Globals.
servers = {}  # Holds output objects.
last_request_for_output = int(time.time())  # Holds last requested output time.

# Initialize view blueprint.
views = Blueprint("views", __name__)


######### Home Page #########

@views.route("/", methods=["GET"])
@views.route("/home", methods=["GET"])
@login_required
def home():
    # Import config data.
    config = configparser.ConfigParser()
    config.read("main.conf")
    text_color = config["aesthetic"]["text_color"]
    graphs_primary = config["aesthetic"]["graphs_primary"]
    graphs_secondary = config["aesthetic"]["graphs_secondary"]
    show_stats = config["aesthetic"].getboolean("show_stats")
    show_barrel_roll = config["aesthetic"].getboolean("show_barrel_roll")

    current_app.logger.info(log_wrap("current_user.username", current_user.username))
    current_app.logger.info(log_wrap("current_user.role", current_user.role))
    current_app.logger.info(log_wrap("current_user.permissions", current_user.permissions))

    config_options = {
        "text_color": text_color,
        "graphs_primary": graphs_primary,
        "graphs_secondary": graphs_secondary,
        "show_stats": show_stats,
        "show_barrel_roll": show_barrel_roll,
    }

    # Kill any lingering background watch processes
    # Used in case console page is clicked away from.
    kill_watchers(last_request_for_output)

    installed_servers = GameServer.query.all()

    current_app.logger.info(log_wrap("config_options", config_options))
    current_app.logger.info(log_wrap("installed_servers", installed_servers))

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
    # Import config data.
    config = configparser.ConfigParser()
    config.read("main.conf")
    text_color = config["aesthetic"]["text_color"]
    terminal_height = config["aesthetic"]["terminal_height"]
    cfg_editor = config["settings"]["cfg_editor"]
    send_cmd = config["settings"].getboolean("send_cmd")
    clear_output_on_reload = config["settings"].getboolean("clear_output_on_reload")

    # Collect args from GET request.
    server_name = request.args.get("server")
    short_cmd = request.args.get("command")
    console_cmd = request.args.get("cmd")

    # Can't load the controls page without a server specified.
    if server_name == None:
        flash("No server specified!", category="error")
        return redirect(url_for("views.home"))

    # Check if user has permissions to game server for controls route.
    if not user_has_permissions(current_user, "controls", server_name):
        return redirect(url_for("views.home"))

    # Check that the submitted server exists in db.
    server = GameServer.query.filter_by(install_name=server_name).first()
    # If game server doesn't exist in db, can't load page for it.
    if server == None:
        flash("Invalid game server name!", category="error")
        return redirect(url_for("views.home"))

    if server.install_type == 'remote':
        if not is_ssh_accessible(server.install_host):
            flash("Unable to access remote server over ssh!", category="error")
            return redirect(url_for("views.home"))

    if not local_install_path_exists(server):
        flash("No game server installation directory found!", category="error")
        return redirect(url_for("views.home"))

    # If config editor is disabled in the main.conf.
    if cfg_editor == "no":
        cfg_paths = []
    else:
        cfg_paths = find_cfg_paths(server.install_path)
        if cfg_paths == "failed":
            flash("Error reading accepted_cfgs.json!", category="error")
            cfg_paths = []

    # Pull in commands list from commands.json file.
    cmds_list = get_commands(server.script_name, send_cmd, current_user)
    # TODO: Remove / change this as a way to check if json file is okay. Right
    # now this is serving the purposes of telling if the json file has become
    # mangled or not, in case users have edited it by hand and left off a comma
    # or something. I should make a dedicated function to check if json data is
    # all good and put that at the top of the route instead.
    if not cmds_list:
        flash("Error loading commands.json file!", category="error")
        return redirect(url_for("views.home"))

    # Object to hold process info from cmd in daemon thread.
    proc_info = ProcInfoVessel()

    # If this is the first time we're ever seeing the server_name then put it
    # and its associated proc_info in the global servers dictionary.
    if not server_name in servers:
        servers[server_name] = proc_info

    # Set the output object to the one stored in the global dictionary.
    proc_info = servers[server_name]
    if clear_output_on_reload == True:
        proc_info.stdout.clear()
        proc_info.stderr.clear()

    script_path = os.path.join(server.install_path, server.script_name)

    # This code block is only triggered in the event the short_cmd param is
    # supplied with the GET request. Aka if a user has clicked one of the
    # control button.
    if short_cmd:
        # Validate short_cmd against contents of commands.json file.
        if not valid_command(short_cmd, server.script_name, send_cmd, current_user):
            flash("Invalid Command!", category="error")
            return redirect(url_for("views.controls", server=server_name))

        # Console option, use tmux capture-pane to get output.
        if short_cmd == "c":
            gs_id = get_gs_id(server)
            active = get_server_status(server, gs_id)
            if not active:
                flash("Server is Off! No Console Output!", category="error")
                return redirect(url_for("views.controls", server=server_name))

            tmux_socket = server.script_name + "-" + gs_id

            # Use daemonized `watch` command to keep live console running.
            cmd = [
                "/usr/bin/watch",
                "-te",
                "/usr/bin/tmux",
                "-L",
                tmux_socket,
                "capture-pane",
                "-pt",
                server.script_name,
            ]
            if should_use_ssh(server):
                cmd = " ".join(cmd)
                pub_key_file = get_ssh_key_file(server.username, server.install_host)
                daemon = Thread(
                    target=run_cmd_ssh, args=(cmd, server.install_host, server.username, pub_key_file, proc_info, current_app.app_context(), None), daemon=True, name="Console"
                )
                daemon.start()
                return redirect(url_for("views.controls", server=server_name))

            daemon = Thread(
                target=run_cmd_popen, args=(cmd, proc_info, current_app.app_context()), daemon=True, name="Console"
            )
            daemon.start()
            return redirect(url_for("views.controls", server=server_name))

        elif short_cmd == "sd":
            # Check if send_cmd is enabled in main.conf.
            if not send_cmd:
                flash("Send console command button disabled!", category="error")
                return redirect(url_for("views.controls", server=server_name))

            if console_cmd == None:
                flash("No command provided!", category="error")
                return redirect(url_for("views.controls", server=server_name))

            # First check if tmux session is running.
            installed_servers = GameServer.query.all()

            # Fetch dict containing all servers and flag specifying if they're running
            # or not via a util function.
            server_status_dict = get_all_server_statuses(installed_servers)
            if not server_status_dict[server_name]:
                flash(
                    "Server is Off! Cannot send commands to console!", category="error"
                )
                return redirect(url_for("views.controls", server=server_name))

            cmd = []
            # If gs not owned by system user, prepend sudo -n -u user to cmd.
            if server.username != USER:
                cmd += sudo_prepend

            cmd += [script_path, short_cmd, console_cmd]
            daemon = Thread(
                target=run_cmd_popen, args=(cmd, proc_info, current_app.app_context()), daemon=True, name="ConsoleCMD"
            )
            daemon.start()
            return redirect(url_for("views.controls", server=server_name))

        else:
            if should_use_ssh(server):
                cmd = f"{script_path} {short_cmd}"
                pub_key_file = get_ssh_key_file(server.username, server.install_host)
                daemon = Thread(
                    target=run_cmd_ssh, args=(cmd, server.install_host, server.username, pub_key_file, proc_info, current_app.app_context()), daemon=True, name="Command"
                )
                daemon.start()
                return redirect(url_for("views.controls", server=server_name))

            cmd = [script_path, short_cmd]
            daemon = Thread(
                target=run_cmd_popen, args=(cmd, proc_info, current_app.app_context()), daemon=True, name="Command"
            )
            daemon.start()
            return redirect(url_for("views.controls", server=server_name))

    current_app.logger.info(log_wrap("server_name", server_name))
    current_app.logger.info(log_wrap("cmds_list", cmds_list))
    current_app.logger.info(log_wrap("text_color", text_color))
    current_app.logger.info(log_wrap("terminal_height", terminal_height))
    current_app.logger.info(log_wrap("SPINNER_COLORS", SPINNER_COLORS))
    current_app.logger.info(log_wrap("cfg_paths", cfg_paths))

    return render_template(
        "controls.html",
        user=current_user,
        server_name=server_name,
        server_commands=cmds_list,
        text_color=text_color,
        terminal_height=terminal_height,
        spinner_colors=SPINNER_COLORS,
        cfg_paths=cfg_paths,
    )


######### Install Page #########

@views.route("/install", methods=["GET", "POST"])
@login_required
def install():
    global servers

    # Import config data.
    config = configparser.ConfigParser()
    config.read("main.conf")
    text_color = config["aesthetic"]["text_color"]
    terminal_height = config["aesthetic"]["terminal_height"]
    create_new_user = config["settings"].getboolean("install_create_new_user")

    # Check if user has permissions to install route.
    if not user_has_permissions(current_user, "install"):
        return redirect(url_for("views.home"))

    # Pull in install server list from game_servers.json file.
    install_list = get_servers()
    if not install_list:
        flash("Error loading game_servers.json file!", category="error")
        return redirect(url_for("views.home"))

    # Initialize blank install_name, used for update-text-area.js.
    install_name = ""

    # Kill any lingering background watch processes if page is reloaded.
    kill_watchers(last_request_for_output)

    # Check for / install the main linuxgsm.sh script.
    lgsmsh = "linuxgsm.sh"
    check_and_get_lgsmsh(f"scripts/{lgsmsh}")

    # Check if any installs are currently running.
    running_installs = get_running_installs()

    # Post logic only triggered after install form submission.
    if request.method == "POST":
        server_script_name = request.form.get("server_name")
        server_full_name = request.form.get("full_name")

        # Make sure required options are supplied.
        for required_form_item in (server_script_name, server_full_name):
            if required_form_item == None:
                flash("Missing Required Form Field!", category="error")
                return redirect(url_for("views.install"))

            # Check input lengths.
            if len(required_form_item) > 150:
                flash("Form field too long!", category="error")
                return redirect(url_for("views.install"))

        # Validate form submission data against install list in json file.
        if not valid_install_options(server_script_name, server_full_name):
            flash("Invalid Installation Option(s)!", category="error")
            return redirect(url_for("views.install"))

        # Make server_full_name a unix friendly directory name.
        server_full_name = server_full_name.replace(" ", "_")
        server_full_name = server_full_name.replace(":", "")

        # Used to pass install_name to frontend js.
        install_name = server_full_name

        # Clobber any previously held proc_info objects for server.
        servers[server_full_name] = ProcInfoVessel()

        # Set the output object to the one stored in the global dictionary.
        output = servers[server_full_name]

        install_exists = GameServer.query.filter_by(
            install_name=server_full_name
        ).first()

        if install_exists:
            flash("An installation by that name already exits.", category="error")
            return redirect(url_for("views.install"))

        # Set Ansible playbook vars.
        ansible_vars = dict()
        ansible_vars["action"] = "install"
        ansible_vars["gs_user"] = USER
        ansible_vars["install_path"] = os.path.join(CWD, f'GameServers/{server_full_name}')
        ansible_vars["server_script_name"] = server_script_name
        ansible_vars["script_paths"] = ""
        ansible_vars["web_lgsm_user"] = USER

        if not create_new_user:
            ansible_vars["same_user"] = "true"
            install_type = 'local' 

        new_game_server = GameServer(
            install_name=server_full_name,
            install_path=ansible_vars["install_path"],
            script_name=server_script_name,
            username=ansible_vars["gs_user"],
            is_container = False,
            install_type = install_type,
            install_host = '127.0.0.1'
        )

        # If install_create_new_user config parameter is true then create a new
        # user for the new game server and set install path to the path in that
        # new users home directory.
        if create_new_user or "CONTAINER" in os.environ:
            install_path = f"/home/{server_script_name}/GameServers/{server_full_name}"
            ansible_vars["gs_user"] = server_script_name
            ansible_vars["install_path"] = install_path
            ansible_vars["script_paths"] = get_user_script_paths(install_path, server_script_name)

        if "CONTAINER" in os.environ:
            # If we're in a container and the path doesn't exist we want to
            # alert the user and tell them the container needs re-built first.
            if not local_install_path_exists(new_game_server):
                flash("Rebuild container first! See docs/docker_info.md for more information.", category="error")
                flash("Run docker-setup.py --add to add an install to the container first, then rebuild!", category="error")
                return redirect(url_for("views.home"))
        else:
            if local_install_path_exists(new_game_server):
                flash("Install directory already exists.", category="error")
                flash(
                    "Did you perhaps have this server installed previously?",
                    category="error",
                )
                return redirect(url_for("views.install"))

        write_ansible_vars_json(ansible_vars)

        # Add the install to the database.
        db.session.add(new_game_server)
        db.session.commit()

        # Update web user's permissions.
        if current_user.role != "admin":
            user_ident = User.query.filter_by(username=current_user.username).first()
            user_perms = json.loads(user_ident.permissions)
            user_perms["servers"].append(server_full_name)
            user_ident.permissions = json.dumps(user_perms)
            db.session.commit()

        cmd = [
            "/usr/bin/sudo",
            "-n",
            os.path.join(CWD, "venv/bin/python"),
            ANSIBLE_CONNECTOR
        ]

        current_app.logger.info(log_wrap("ansible_vars", ansible_vars))
        current_app.logger.info(log_wrap("cmd", cmd))
        current_app.logger.info(log_wrap("servers", servers))

        install_daemon = Thread(
            target=run_cmd_popen,
            args=(cmd, output, current_app.app_context()),
            daemon=True,
            name=f"Install_{server_full_name}",
        )
        install_daemon.start()

    elif request.method == "GET":
        server_name = request.args.get("server")
        cancel = request.args.get("cancel")
        if server_name != None:
            if not valid_server_name(server_name):
                flash("Invalid Option!", category="error")
                return redirect(url_for("views.install"))

            install_name = server_name

            if cancel == "true":
                # Check if install thread is still running.
                thread_name = "Install_" + server_name
                if thread_name not in running_installs:
                    flash(
                        f"Install for {server_name} not currently running!",
                        category="error",
                    )
                    return redirect(url_for("views.install"))

                output = servers[server_name]
                current_app.logger.info(log_wrap("output", output))

                if output.pid:
                    cancel_install(output)

    return render_template(
        "install.html",
        user=current_user,
        servers=install_list,
        text_color=text_color,
        spinner_colors=SPINNER_COLORS,
        install_name=install_name,
        terminal_height=terminal_height,
        running_installs=running_installs,
    )


######### API Server Statuses #########

@views.route("/api/server-status", methods=["GET"])
@login_required
def get_status():
# TODO: Write permissions controls for these api routes.
#    if not user_has_permissions(current_user, "server-statuses"):
#        return redirect(url_for("views.home"))

    # Collect args from GET request.
    server_id = request.args.get("id")

    if server_id == None:
        resp_dict = {"error": "No id supplied"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
        )
        return response

    server = GameServer.query.get(server_id)
    if server == None:
        resp_dict = {"error": "Invalid id"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
        )
        return response

    server_status = get_server_status(server)
    resp_dict = {"id": int(server_id), "status": server_status}
    response = Response(
        json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
    )
    return response


######### API System Usage #########

@views.route("/api/system-usage", methods=["GET"])
@login_required
def get_stats():
# TODO: Write permissions controls for these api routes.
#    if not user_has_permissions(current_user, "system-usage"):
#        return redirect(url_for("views.home"))

    server_stats = get_server_stats()
    response = Response(
        json.dumps(server_stats, indent=4), status=200, mimetype="application/json"
    )
    return response


######### API CMD Output Page #########

@views.route("/api/cmd-output", methods=["GET"])
@login_required
def no_output():
# TODO: Write permissions controls for these api routes.
#    if not user_has_permissions(current_user, "cmd-output"):
#        return redirect(url_for("views.home"))

    global servers

    # Collect args from GET request.
    server_name = request.args.get("server")

    # Can't load the controls page without a server specified.
    if server_name == None:
        resp_dict = {"error": "eer can't load page n'@"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
        )
        return response

    # Can't do anything if we don't recognize the server_name.
    if server_name not in servers:
        resp_dict = {"error": "eer never heard of em"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
        )
        return response

    # Reset the last requested output time.
    last_request_for_output = int(time.time())

    # If its a server in the servers dict set the output object to the
    # one from that dictionary.
    if server_name in servers:
        output = servers[server_name]

    # Returns json for used by ajax code on /controls route.
    response = Response(output.toJSON(), status=200, mimetype="application/json")
    return response


######### Settings Page #########

@views.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    # Kill any lingering background watch processes in case console page is
    # clicked away fromleft.
    kill_watchers(last_request_for_output)

    # Import config data.
    # TODO: Make functions for loading in config options for functions.
    config = configparser.ConfigParser()
    config.read("main.conf")
    text_color = config["aesthetic"]["text_color"]
    terminal_height = config["aesthetic"]["terminal_height"]
    remove_files = config["settings"].getboolean("remove_files")
    clear_output_on_reload = config["settings"].getboolean("clear_output_on_reload")
    graphs_primary = config["aesthetic"]["graphs_primary"]
    graphs_secondary = config["aesthetic"]["graphs_secondary"]
    show_stats = config["aesthetic"].getboolean("show_stats")
    install_create_new_user = config["settings"].getboolean("install_create_new_user")

    # Check if user has permissions to settings route.
    if not user_has_permissions(current_user, "settings"):
        return redirect(url_for("views.home"))

    config_options = {
        "text_color": text_color,
        "terminal_height": terminal_height,
        "remove_files": remove_files,
        "clear_output_on_reload": clear_output_on_reload,
        "graphs_primary": graphs_primary,
        "graphs_secondary": graphs_secondary,
        "show_stats": show_stats,
        "install_create_new_user": install_create_new_user,
    }

    current_app.logger.info(log_wrap("config_options", config_options))

    if request.method == "GET":
        return render_template(
            "settings.html",
            user=current_user,
            system_user=USER,
            config_options=config_options,
        )

    text_color_pref = request.form.get("text_color")
    file_pref = request.form.get("delete_files")
    clear_output_pref = request.form.get("clear_output_on_reload")
    height_pref = request.form.get("terminal_height")
    update_weblgsm = request.form.get("update_weblgsm")
    graphs_primary_pref = request.form.get("graphs_primary")
    graphs_secondary_pref = request.form.get("graphs_secondary")
    show_stats_pref = request.form.get("show_stats")
    install_new_user_pref = request.form.get("install_new_user")

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
    config["aesthetic"]["terminal_height"] = terminal_height
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

    with open("main.conf", "w") as configfile:
        config.write(configfile)

    # Update's the weblgsm.
    if update_weblgsm:
        status = update_self()
        flash("Settings Updated!")
        if "Error:" in status:
            flash(status, category="error")
            return redirect(url_for("views.settings"))

        flash(status)

        # Restart daemon thread sleeps for 5 seconds then restarts app.
        cmd = ["./web-lgsm.py", "--restart"]
        restart_daemon = Thread(
            target=restart_self, args=(cmd, ProcInfoVessel(), current_app.app_context()), daemon=True, name="restart"
        )
        restart_daemon.start()
        return redirect(url_for("views.settings"))

    # Debug messages.
    current_app.logger.info(log_wrap("text_color_pref", text_color_pref))
    current_app.logger.info(log_wrap("file_pref", file_pref))
    current_app.logger.info(log_wrap("height_pref", height_pref))
    current_app.logger.info(log_wrap("update_weblgsm", update_weblgsm))
    current_app.logger.info(log_wrap("graphs_primary_pref", graphs_primary_pref))
    current_app.logger.info(log_wrap("graphs_secondary_pref", graphs_secondary_pref))
    current_app.logger.info(log_wrap("show_stats_pref", show_stats_pref))
    current_app.logger.info(log_wrap("install_new_user_pref", install_new_user_pref))

    flash("Settings Updated!")
    return redirect(url_for("views.settings"))


######### About Page #########

@views.route("/about", methods=["GET"])
@login_required
def about():
    # Kill any lingering background watch processes.
    # In case console page is clicked away from.
    kill_watchers(last_request_for_output)

    # Import config data.
    config = configparser.ConfigParser()
    config.read("main.conf")
    text_color = config["aesthetic"]["text_color"]

    return render_template("about.html", user=current_user, text_color=text_color)


######### Add Page #########

@views.route("/add", methods=["GET", "POST"])
@login_required
def add():
    # Import config data.
    config = configparser.ConfigParser()
    config.read("main.conf")
    remove_files = config["settings"].getboolean("remove_files")

    # Check if user has permissions to add route.
    if not user_has_permissions(current_user, "add"):
        return redirect(url_for("views.home"))

    # Kill any lingering background watch processes in case console page is
    # clicked away fromleft.
    kill_watchers(last_request_for_output)

    # Set default status_code.
    status_code = 200

    if request.method == "POST":
        install_name = request.form.get("install_name")
        install_path = request.form.get("install_path")
        script_name = request.form.get("script_name")
        username = request.form.get("username")
        install_type = request.form.get("install_type")
        install_host = request.form.get("install_host")

        # Check all required args are submitted.
        for required_form_item in (install_name, install_path, script_name, install_type):
            if required_form_item == None or required_form_item == "":
                flash("Missing required form field(s)!", category="error")
                return render_template("add.html", user=current_user), 400

            # Check input lengths.
            if len(required_form_item) > 150:
                flash("Form field too long!", category="error")
                return render_template("add.html", user=current_user), 400

        # Validate install_type.
        if not valid_install_type(install_type):
            flash("Invalid install type!", category="error")
            return render_template("add.html", user=current_user), 400

        if install_type == 'remote':
            if install_host == None or install_host == "":
                flash("Missing required form field(s)!", category="error")
                return render_template("add.html", user=current_user), 400

            if not is_ssh_accessible(install_host):
                flash("Server does not appear to be SSH accessible!", category="error")
                return render_template("add.html", user=current_user), 400

        # Set default user if none provided.
        if username == None or username == "":
            username = USER

        if len(username) > 150:
            flash("Form field too long!", category="error")
            return render_template("add.html", user=current_user), 400

        if install_type == 'local':
            # Returns None if not valid username.
            if get_uid(username) == None:
                flash("User not found on system!", category="error")
                status_code = 400
                return render_template("add.html", user=current_user), status_code

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
        # TODO: Do more here to prevent people from putting in weird names.
        install_name = install_name.replace(" ", "_")

        install_exists = GameServer.query.filter_by(install_name=install_name).first()

        if install_exists:
            flash("An installation by that name already exits.", category="error")
            status_code = 400
            return render_template("add.html", user=current_user), status_code

        if not valid_script_name(script_name):
            flash("Invalid game server script file name!", category="error")
            status_code = 400
            return render_template("add.html", user=current_user), status_code

        script_path = os.path.join(install_path, script_name)
        # Check script path exists.
        # TODO: Write this function for over ssh.
#        check_script_path_exists(script_path)

        if install_type == 'local':
            install_host = '127.0.0.1'

        if install_type == 'local' and USER != username:
            # Get a list of all game servers installed for this system user.
            user_script_paths = get_user_script_paths(install_path, script_name)

            # Set Ansible playbook vars.
            ansible_vars = dict()
            ansible_vars["action"] = "create"
            ansible_vars["gs_user"] = username
            ansible_vars["script_paths"] = user_script_paths
            ansible_vars["web_lgsm_user"] = USER
            write_ansible_vars_json(ansible_vars)

            current_app.logger.info(log_wrap("ansible_vars", ansible_vars))

            cmd = [
                "/usr/bin/sudo",
                "-n",
                os.path.join(CWD, "venv/bin/python"),
                ANSIBLE_CONNECTOR
            ]
            run_cmd_popen(cmd)

        if install_type == 'remote':
            pubkey = get_ssh_key_file(username, install_host)
            if pubkey == None:
                flash(f"Problem generating new ssh keys!", category="error")
                return redirect(url_for("views.add"))

            flash(f"Add this key to the remote hosts ~/.ssh/authorized_keys file:  {pubkey}")

        # Add the install to the database, then redirect home.
        new_game_server = GameServer(
            install_name=install_name,
            install_path=install_path,
            script_name=script_name,
            username=username,
            install_type=install_type,
            install_host=install_host
        )
        db.session.add(new_game_server)
        db.session.commit()

        current_app.logger.info(log_wrap("install_name", install_name))
        current_app.logger.info(log_wrap("install_path", install_path))
        current_app.logger.info(log_wrap("script_name", script_name))
        current_app.logger.info(log_wrap("username", username))

        flash("Game server added!")
        return redirect(url_for("views.home"))

    return render_template("add.html", user=current_user), status_code


######### Delete Route #########


@views.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    global servers

    # TODO: Should eventually make this whole function work via IDs instead of
    # server names. Will get there eventually.
    # Import config data.
    config = configparser.ConfigParser()
    config.read("main.conf")
    remove_files = config["settings"].getboolean("remove_files")

    def del_wrap(server_name):
        """Wraps up delete logic used below"""
        # Check if user has permissions to delete route & server.
        if not user_has_permissions(current_user, "delete", server_name):
            return redirect(url_for("views.home"))

        server = GameServer.query.filter_by(install_name=server_name).first()
        if server == None:
            flash("No such server found!", category="error")
            return redirect(url_for("views.home"))

        current_app.logger.info(log_wrap("server_name", server_name))
        current_app.logger.info(log_wrap("servers", servers))
        current_app.logger.info(log_wrap("server.id", server.id))
        current_app.logger.info(log_wrap("server.install_name", server.install_name))
        current_app.logger.info(log_wrap("server.username", server.username))
        current_app.logger.info(log_wrap("server.install_path", server.install_path))

        if server:
            if server_name in servers:
                del servers[server_name]
            proc_info = ProcInfoVessel()

            current_app.logger.info(log_wrap("servers", servers))

            del_server(server, remove_files)

    # Delete via POST is for multiple deletions.
    # Post submissions come from delete toggles on home page.
    if request.method == "POST":
        for server_id, server_name in request.form.items():
            del_wrap(server_name)
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

    # Import config data.
    config = configparser.ConfigParser()
    config.read("main.conf")
    text_color = config["aesthetic"]["text_color"]
    terminal_height = config["aesthetic"]["terminal_height"]

    if config["settings"]["cfg_editor"] == "no":
        flash("Config Editor Disabled", category="error")
        return redirect(url_for("views.home"))

    # Collect args from POST request.
    server_name = request.form.get("server")
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

    # Checks that install dir exists.
    if not os.path.isdir(server.install_path):
        flash("No game server installation directory found!", category="error")
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
            flash("Config Updated!", category="success")
        except:
            flash("Error writing to config!", category="error")

    # Read in file contents from cfg file.
    file_contents = ""
    # Try except incase problem with file.
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
        text_color=text_color,
        terminal_height=terminal_height,
        server_name=server_name,
        cfg_file=cfg_path,
        file_contents=file_contents,
        cfg_file_name=cfg_file,
    )
