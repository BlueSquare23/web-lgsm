import os
import re
import sys
import json
import time
import signal
import shutil
import getpass
import configparser
from . import db
from .utils import *
from .models import *
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
)

# Constants.
CWD = os.getcwd()
USER = getpass.getuser()
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
ANSIBLE_CONNECTOR = os.path.join(CWD, "playbooks/sudo_ansible_connector.py")

# Globals.
servers = {}  # Holds output objects.
last_request_for_output = int(time.time())  # Holds last requested output time.
debug = False
verbosity = 0

# Initialize view blueprint.
views = Blueprint("views", __name__)


######### Home Page #########

@views.route("/", methods=["GET"])
@views.route("/home", methods=["GET"])
@login_required
def home():
    global debug
    global verbosity

    # Import config data.
    config = configparser.ConfigParser()
    config.read("main.conf")
    text_color = config["aesthetic"]["text_color"]
    graphs_primary = config["aesthetic"]["graphs_primary"]
    graphs_secondary = config["aesthetic"]["graphs_secondary"]
    show_stats = config["aesthetic"].getboolean("show_stats")
    show_barrel_roll = config["aesthetic"].getboolean("show_barrel_roll")
    debug = config["debug"].getboolean("debug")
    v = config["debug"]["verbosity"]
    verbosity = get_verbosity(v)

    debug_handler("current_user.username", current_user.username, debug)
    debug_handler("current_user.role", current_user.role, debug)
    debug_handler("current_user.permissions", current_user.permissions, debug)

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
    servers_to_users = {}
    for server in installed_servers:
        servers_to_users[server.install_name] = server.username

    # Fetch dict containing all servers and flag specifying if they're running
    # or not via a util function.
    server_status_dict = get_server_statuses()

    debug_handler("config_options", config_options, debug)
    debug_handler("installed_servers", installed_servers, debug)
    debug_handler("servers_to_users", servers_to_users, debug)
    debug_handler("server_status_dict", server_status_dict, debug)

    return render_template(
        "home.html",
        user=current_user,
        servers_to_users=servers_to_users,
        server_status_dict=server_status_dict,
        config_options=config_options,
    )


######### XtermJS Test Page #########

@views.route("/xtermjs", methods=["GET"])
@login_required
def xtermjs():
    global servers

    server_name = "testingxtermjs"
    if not server_name in servers:
        proc_info = ProcInfoVessel()
        servers[server_name] = proc_info

    # Set the output object to the one stored in the global dictionary.
    output = servers[server_name]

    cmd = ["/home/blue/Projects/web-lgsm/scripts/random.sh"]
    daemon = Thread(target=run_cmd_popen, args=(cmd, output), daemon=True, name="Command")

    daemon.start()
    return render_template("xtermjs.html", user=current_user, server_name=server_name)


######### Controls Page #########

@views.route("/controls", methods=["GET"])
@login_required
def controls():
    global debug
    global verbosity

    # Import config data.
    config = configparser.ConfigParser()
    config.read("main.conf")
    text_color = config["aesthetic"]["text_color"]
    terminal_height = config["aesthetic"]["terminal_height"]
    cfg_editor = config["settings"]["cfg_editor"]
    send_cmd = config["settings"].getboolean("send_cmd")
    debug = config["debug"].getboolean("debug")
    v = config["debug"]["verbosity"]
    verbosity = get_verbosity(v)

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

    if not install_path_exists(server.install_path):
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

    # Object to hold output from any running daemon threads.
    proc_info = ProcInfoVessel()

    # If this is the first time we're ever seeing the server_name then put it
    # and its associated proc_info in the global servers dictionary.
    if not server_name in servers:
        servers[server_name] = proc_info

    # Set the output object to the one stored in the global dictionary.
    proc_info = servers[server_name]

    script_path = os.path.join(server.install_path, server.script_name)

    # This code block is only triggered in the event the short_cmd param is
    # supplied with the GET request. Aka if a user has clicked one of the
    # control button.
    if short_cmd:
        # For running cmds as alt users.
        sudo_prepend = ["/usr/bin/sudo", "-n", "-u", server.username]

        # Validate short_cmd against contents of commands.json file.
        if not valid_command(short_cmd, server.script_name, send_cmd, current_user):
            flash("Invalid Command!", category="error")
            return redirect(url_for("views.controls", server=server_name))

        # Console option, use tmux capture-pane to get output.
        if short_cmd == "c":
            # First check if tmux session is running.
            installed_servers = GameServer.query.all()

            server_status_dict = get_server_statuses()
            if server_status_dict[server_name] == "inactive":
                flash("Server is Off! No Console Output!", category="error")
                return redirect(url_for("views.controls", server=server_name))

            servers_to_sockets = get_sockets()
            if servers_to_sockets[server.install_name] == None:
                flash("Cannot find socket for server!", category="error")
                return redirect(url_for("views.controls", server=server_name))

            tmux_socket = server.script_name + '-' + servers_to_sockets[server.install_name]

            cmd = []
            # If gs not owned by system user, prepend sudo -n -u user to cmd.
            if server.username != USER:
                cmd += sudo_prepend

            # Use daemonized `watch` command to keep live console running.
            cmd += [
                "/usr/bin/watch",
                "-te",
                "/usr/bin/tmux",
                "-L",
                tmux_socket,
                "capture-pane",
                "-pt",
                server.script_name,
            ]
            daemon = Thread(
                target=run_cmd_popen, args=(cmd, proc_info), daemon=True, name="Console"
            )
            daemon.start()
            return redirect(url_for("views.controls", server=server_name))

        elif short_cmd == "sd":
            # Check if send_cmd is enabled in main.conf.
            if send_cmd == "no":
                flash("Send console command button disabled!", category="error")
                return redirect(url_for("views.controls", server=server_name))

            if console_cmd == None:
                flash("No command provided!", category="error")
                return redirect(url_for("views.controls", server=server_name))

            # First check if tmux session is running.
            installed_servers = GameServer.query.all()

            # Fetch dict containing all servers and flag specifying if they're running
            # or not via a util function.
            server_status_dict = get_server_statuses()
            if server_status_dict[server_name] == "inactive":
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
                target=run_cmd_popen, args=(cmd, proc_info), daemon=True, name="ConsoleCMD"
            )
            daemon.start()
            return redirect(url_for("views.controls", server=server_name))

        # If its not the console or send command
        else:
            cmd = []
            # If gs not owned by system user, prepend sudo -n -u user to cmd.
            if server.username != USER:
                cmd += sudo_prepend

            cmd += [script_path, short_cmd]
            daemon = Thread(
                target=run_cmd_popen, args=(cmd, proc_info), daemon=True, name="Command"
            )
            daemon.start()
            return redirect(url_for("views.controls", server=server_name))

    if debug and verbosity >= 1:
        print(f"##### debug server_name {server_name}")
        print(f"##### debug cmds_list {cmds_list}")
        print(f"##### debug text_color {text_color}")
        print(f"##### debug terminal_height {terminal_height}")
        print(f"##### debug SPINNER_COLORS {SPINNER_COLORS}")
        print(f"##### debug cfg_paths {cfg_paths}")

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
    global debug
    global verbosity

    # Import config data.
    config = configparser.ConfigParser()
    config.read("main.conf")
    text_color = config["aesthetic"]["text_color"]
    terminal_height = config["aesthetic"]["terminal_height"]
    create_new_user = config["settings"].getboolean("install_create_new_user")
    debug = config["debug"].getboolean("debug")
    v = config["debug"]["verbosity"]
    verbosity = get_verbosity(v)

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

        # If install_create_new_user config parameter is true then create a new
        # user for the new game server and set install path to the path in that
        # new users home directory.
        if create_new_user:
            ansible_vars["gs_user"] = server_script_name
            ansible_vars["install_path"] = os.path.join(
                f"/home/{server_script_name}",
                f"GameServers/{server_full_name}"
            )
            ansible_vars["script_paths"] = get_user_script_paths(
                ansible_vars["install_path"], server_script_name
            )

        if install_path_exists(ansible_vars["install_path"]):
            flash("Install directory already exists.", category="error")
            flash(
                "Did you perhaps have this server installed previously?",
                category="error",
            )
            return redirect(url_for("views.install"))

        write_ansible_vars_json(ansible_vars)

        # Add the install to the database.
        new_game_server = GameServer(
            install_name=server_full_name,
            install_path=ansible_vars["install_path"],
            script_name=server_script_name,
            username=ansible_vars["gs_user"],
        )
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

        debug_handler("ansible_vars", ansible_vars, debug)
        debug_handler("cmd", cmd, debug)
        debug_handler("servers", servers, debug)

        install_daemon = Thread(
            target=run_cmd_popen,
            args=(cmd, output),
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
                if verbosity >= 2:
                    debug_handler("output", output, debug)

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
    global debug
    global verbosity

    # Kill any lingering background watch processes in case console page is
    # clicked away fromleft.
    kill_watchers(last_request_for_output)

    # Import config data.
    config = configparser.ConfigParser()
    config.read("main.conf")
    text_color = config["aesthetic"]["text_color"]
    terminal_height = config["aesthetic"]["terminal_height"]
    remove_files = config["settings"].getboolean("remove_files")
    graphs_primary = config["aesthetic"]["graphs_primary"]
    graphs_secondary = config["aesthetic"]["graphs_secondary"]
    show_stats = config["aesthetic"].getboolean("show_stats")
    install_create_new_user = config["settings"].getboolean("install_create_new_user")
    debug = config["debug"].getboolean("debug")
    v = config["debug"]["verbosity"]
    verbosity = get_verbosity(v)

    # Check if user has permissions to settings route.
    if not user_has_permissions(current_user, "settings"):
        return redirect(url_for("views.home"))

    config_options = {
        "text_color": text_color,
        "terminal_height": terminal_height,
        "remove_files": remove_files,
        "graphs_primary": graphs_primary,
        "graphs_secondary": graphs_secondary,
        "show_stats": show_stats,
        "install_create_new_user": install_create_new_user,
    }

    debug_handler("config_options", config_options, debug)

    if request.method == "GET":
        return render_template(
            "settings.html",
            user=current_user,
            system_user=USER,
            config_options=config_options,
        )

    text_color_pref = request.form.get("text_color")
    file_pref = request.form.get("delete_files")
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
            target=restart_self, args=(cmd,), daemon=True, name="restart"
        )
        restart_daemon.start()
        return redirect(url_for("views.settings"))

    # Debug messages.
    debug_handler("text_color_pref", text_color_pref, debug)
    debug_handler("file_pref", file_pref, debug)
    debug_handler("height_pref", height_pref, debug)
    debug_handler("update_weblgsm", update_weblgsm, debug)
    debug_handler("graphs_primary_pref", graphs_primary_pref, debug)
    debug_handler("graphs_secondary_pref", graphs_secondary_pref, debug)
    debug_handler("show_stats_pref", show_stats_pref, debug)
    debug_handler("install_new_user_pref", install_new_user_pref, debug)

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
    global debug
    global verbosity

    # Import config data.
    config = configparser.ConfigParser()
    config.read("main.conf")
    remove_files = config["settings"].getboolean("remove_files")

    debug = config["debug"].getboolean("debug")
    v = config["debug"]["verbosity"]
    verbosity = get_verbosity(v)

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

        # Check all required args are submitted.
        for required_form_item in (install_name, install_path, script_name):
            if required_form_item == None or required_form_item == "":
                flash("Missing required form field(s)!", category="error")
                status_code = 400
                return render_template("add.html", user=current_user), status_code

            # Check input lengths.
            if len(required_form_item) > 150:
                flash("Form field too long!", category="error")
                status_code = 400
                return render_template("add.html", user=current_user), status_code

        # Set default user if none provided.
        if username == None or username == "":
            username = USER

        if len(username) > 150:
            flash("Form field too long!", category="error")
            status_code = 400
            return render_template("add.html", user=current_user), status_code

        # Returns None if not valid username.
        if get_uid(username) == None:
            flash("User not found on system!", category="error")
            status_code = 400
            return render_template("add.html", user=current_user), status_code

        # Make install name unix friendly for dir creation.
        install_name = install_name.replace(" ", "_")

        install_exists = GameServer.query.filter_by(install_name=install_name).first()

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

        if install_exists:
            flash("An installation by that name already exits.", category="error")
            status_code = 400
            return render_template("add.html", user=current_user), status_code

        # TODO: This doesn't work anymore, fix. Can't check dir for other users.
        #        elif not os.path.exists(install_path) or not os.path.isdir(install_path):
        #            flash('Directory path does not exist.', category='error')
        #            status_code = 400
        #            return render_template("add.html", user=current_user), status_code

        if not valid_script_name(script_name):
            flash("Invalid game server script file name!", category="error")
            status_code = 400
            return render_template("add.html", user=current_user), status_code

        script_path = os.path.join(install_path, script_name)
        # TODO: This doesn't work anymore, fix. Can't check dir for other users.
        #        if not os.path.exists(script_path) or \
        #                not os.path.isfile(script_path):
        #            flash('Script file does not exist.', category='error')
        #            status_code = 400
        #            return render_template("add.html", user=current_user), status_code

        # Add sudoers rules automatically if game server not owned by web-lgsm
        # system user. To the user, note there is a slight problem with this
        # code. If you try to add a game server as some user that's not allowed
        # by the validate_gs_user.yml playbook (aka not a mcserver type name)
        # then it'll fail.
        if USER != username:
            # Get a list of all game servers installed for this system user.
            user_script_paths = get_user_script_paths(install_path, script_name)

            # Set Ansible playbook vars.
            ansible_vars = dict()
            ansible_vars["action"] = "create"
            ansible_vars["gs_user"] = username
            ansible_vars["script_paths"] = user_script_paths
            ansible_vars["web_lgsm_user"] = USER
            write_ansible_vars_json(ansible_vars)

            debug_handler("ansible_vars", ansible_vars, debug)

            cmd = [
                "/usr/bin/sudo",
                "-n",
                os.path.join(CWD, "venv/bin/python"),
                ANSIBLE_CONNECTOR
            ]
            # TODO: Add debug options to print this hidden output.
            run_cmd_popen(cmd)

        # Add the install to the database, then redirect home.
        new_game_server = GameServer(
            install_name=install_name,
            install_path=install_path,
            script_name=script_name,
            username=username,
        )
        db.session.add(new_game_server)
        db.session.commit()

        debug_handler("install_name", install_name, debug)
        debug_handler("install_path", install_path, debug)
        debug_handler("script_name", script_name, debug)
        debug_handler("username", username, debug)

        flash("Game server added!")
        return redirect(url_for("views.home"))

    return render_template("add.html", user=current_user), status_code


######### Delete Route #########


@views.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    global servers
    global debug
    global verbosity

    # TODO: Should eventually make this whole function work via IDs instead of
    # server names. Will get there eventually.
    # Import config data.
    config = configparser.ConfigParser()
    config.read("main.conf")
    remove_files = config["settings"].getboolean("remove_files")
    debug = config["debug"].getboolean("debug")
    v = config["debug"]["verbosity"]
    verbosity = get_verbosity(v)

    def del_wrap(server_name):
        """Wraps up delete logic used below"""
        # Check if user has permissions to delete route & server.
        if not user_has_permissions(current_user, "delete", server_name):
            return redirect(url_for("views.home"))

        server = GameServer.query.filter_by(install_name=server_name).first()
        if server == None:
            flash("No such server found!", category="error")
            return redirect(url_for("views.home"))

        debug_handler("server_name", server_name, debug)
        debug_handler("servers", servers, debug)
        debug_handler("server.id", server.id, debug)
        debug_handler("server.install_name", server.install_name, debug)
        debug_handler("server.username", server.username, debug)
        debug_handler("server.install_path", server.install_path, debug)

        if server:
            # TODO: Add debug level 2 hidden output printing here.
            if server_name in servers:
                del servers[server_name]
            proc_info = ProcInfoVessel()

            debug_handler("servers", servers, debug)

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
    global debug
    global verbosity

    # NOTE: The abbreviation cfg will be used to refer to any lgsm game server
    # specific config files. Whereas, the word config will be used to refer to
    # any web-lgsm config info.

    # Import config data.
    config = configparser.ConfigParser()
    config.read("main.conf")
    text_color = config["aesthetic"]["text_color"]
    terminal_height = config["aesthetic"]["terminal_height"]
    debug = config["debug"].getboolean("debug")
    v = config["debug"]["verbosity"]
    verbosity = get_verbosity(v)

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
