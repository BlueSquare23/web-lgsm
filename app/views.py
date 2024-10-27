import os
import re
import sys
import json
import time
import shutil
import getpass
import subprocess
import configparser
from . import db
from .utils import *
from .models import *
from threading import Thread
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, flash, url_for, \
                                redirect, Response, send_from_directory, jsonify

# Globals dictionaries to hold output objects.
GAME_SERVERS = {}
INSTALL_SERVERS = {}

# Global last requested output time.
last_request_for_output = int(time.time())

# Initialize view blueprint.
views = Blueprint("views", __name__)


######### Home Page #########

@views.route("/", methods=['GET'])
@views.route("/home", methods=['GET'])
@login_required
def home():
    # Import config data.
    config = configparser.ConfigParser()
    config.read('main.conf')
    text_color = config['aesthetic']['text_color']
    graphs_primary = config['aesthetic']['graphs_primary']
    graphs_secondary = config['aesthetic']['graphs_secondary']
    show_stats = config['aesthetic'].getboolean('show_stats')
    show_barrel_roll = config['aesthetic'].getboolean('show_barrel_roll')

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
        # Account for legacy db's that don't have a user field.
        if server.username == None:
            server.username = getpass.getuser()

        servers_to_users[server.install_name] = server.username

    # Fetch dict containing all servers and flag specifying if they're running
    # or not via a util function.
    server_status_dict = get_server_statuses(installed_servers)

    return render_template("home.html", user=current_user, \
                        servers_to_users=servers_to_users, \
                        server_status_dict=server_status_dict, \
                        config_options=config_options)


######### Controls Page #########

@views.route("/controls", methods=['GET'])
@login_required
def controls():
    # Import config data.
    config = configparser.ConfigParser()
    config.read('main.conf')
    text_color = config['aesthetic']['text_color']
    text_area_height = config['aesthetic']['text_area_height']
    cfg_editor = config['settings']['cfg_editor']
    send_cmd = config['settings']['send_cmd']

    # Collect args from GET request.
    server_name = request.args.get("server")
    script_arg = request.args.get("command")
    console_cmd = request.args.get("cmd")

    # Can't load the controls page without a server specified.
    if server_name == None:
        flash("No server specified!", category="error")
        return redirect(url_for('views.home'))

    # Check that the submitted server exists in db.
    server = GameServer.query.filter_by(install_name=server_name).first()
    # If game server doesn't exist in db, can't load page for it.
    if server == None:
        flash("Invalid game server name!", category="error")
        return redirect(url_for('views.home'))

    # Checks that install dir exists.
    if not os.path.isdir(server.install_path):
        flash("No game server installation directory found!", category="error")
        return redirect(url_for('views.home'))

    # If config editor is disabled in the main.conf.
    if cfg_editor == 'no':
        cfg_paths = []
    else:
        cfg_paths = find_cfg_paths(server.install_path)
        if cfg_paths == "failed":
            flash("Error reading accepted_cfgs.json!", category="error")
            cfg_paths = []

    # Pull in commands list from commands.json file.
    commands_list = get_commands(server.script_name, send_cmd)
    if not commands_list:
        flash('Error loading commands.json file!', category='error')
        return redirect(url_for('views.home'))

    # Bootstrap spinner colors.
    bs_colors = ['primary', 'secondary', 'success', 'danger', 'warning', \
                                                        'info', 'light']

    # Object to hold output from any running daemon threads.
    output_obj = OutputContainer([''], False)

    # If this is the first time we're ever seeing the server_name then put it
    # and its associated output_obj in the global GAME_SERVERS dictionary.
    if not server_name in GAME_SERVERS:
        GAME_SERVERS[server_name] = output_obj

    # Set the output object to the one stored in the global dictionary.
    output = GAME_SERVERS[server_name]

    script_path = server.install_path + '/' + server.script_name

    # This code block is only triggered in the event the script_arg param is
    # supplied with the GET request. Aka if a user has clicked one of the
    # control button.
    if script_arg:
        # For running cmds as alt users.
        system_user = getpass.getuser()
        sudo_prepend = ['/usr/bin/sudo', '-n', '-u', server.username]

        # Account for legacy db's that don't have a user field.
        if server.username == None:
            server.username = getpass.getuser()

        # Validate script_arg against contents of commands.json file.
        if is_invalid_command(script_arg, server.script_name, send_cmd):
            flash("Invalid Command!", category="error")
            return redirect(url_for('views.controls', server=server_name))

        # Console option, use tmux capture-pane to get output.
        if script_arg == "c":
            # First check if tmux session is running.
            installed_servers = GameServer.query.all()

            # Account for legacy db's that don't have a user field.
            for server in installed_servers:
                if server.username == None:
                    server.username = getpass.getuser()

            # Fetch dict containing all servers and flag specifying if they're running
            # or not via a util function.
            server_status_dict = get_server_statuses(installed_servers)
            if server_status_dict[server_name] == 'inactive':
                flash("Server is Off! No Console Output!", category='error')
                return redirect(url_for('views.controls', server=server_name))

            tmux_socket = get_socket_for_gs(server)
            if tmux_socket == None:
                flash("Cannot find socket for server!", category='error')
                return redirect(url_for('views.controls', server=server_name))

            cmd = []
            # If gs not owned by system user, prepend sudo -n -u user to cmd.
            if server.username != system_user:
                cmd += sudo_prepend

            # Use daemonized `watch` command to keep live console running.
            cmd += ['/usr/bin/watch', '-te', '/usr/bin/tmux', '-L', tmux_socket, \
                                        'capture-pane', '-pt', server.script_name]
            daemon = Thread(target=shell_exec, args=(server.install_path, cmd, \
                                    output), daemon=True, name='Console')
            daemon.start()
            return redirect(url_for('views.controls', server=server_name))

        elif script_arg == "sd":
            # Check if send_cmd is enabled in main.conf.
            if send_cmd == 'no':
                flash("Send console command button disabled!", category='error')
                return redirect(url_for('views.controls', server=server_name))

            if console_cmd == None:
                flash("No command provided!", category='error')
                return redirect(url_for('views.controls', server=server_name))

            # First check if tmux session is running.
            installed_servers = GameServer.query.all()

            # Account for legacy db's that don't have a user field.
            for server in installed_servers:
                if server.username == None:
                    server.username = getpass.getuser()

            # Fetch dict containing all servers and flag specifying if they're running
            # or not via a util function.
            server_status_dict = get_server_statuses(installed_servers)
            if server_status_dict[server_name] == 'inactive':
                flash("Server is Off! Cannot send commands to console!", category='error')
                return redirect(url_for('views.controls', server=server_name))

            cmd = []
            # If gs not owned by system user, prepend sudo -n -u user to cmd.
            if server.username != system_user:
                cmd += sudo_prepend

            cmd += [script_path, script_arg, console_cmd]
            daemon = Thread(target=shell_exec, args=(server.install_path, cmd, \
                                    output), daemon=True, name='ConsoleCMD')
            daemon.start()
            return redirect(url_for('views.controls', server=server_name))
            
        # If its not the console or send command
        else:
            cmd = []
            # If gs not owned by system user, prepend sudo -n -u user to cmd.
            if server.username != system_user:
                cmd += sudo_prepend

            cmd += [script_path, script_arg]
            daemon = Thread(target=shell_exec, args=(server.install_path, cmd, \
                                    output), daemon=True, name='Command')
            daemon.start()
            return redirect(url_for('views.controls', server=server_name))

    # Default to no refresh.
    refresh = False

    return render_template("controls.html", user=current_user, \
        server_name=server_name, server_commands=commands_list, \
        text_color=text_color, text_area_height=text_area_height, \
                      bs_colors=bs_colors, cfg_paths=cfg_paths)


######### Install Page #########

@views.route("/install", methods=['GET', 'POST'])
@login_required
def install():
    # Import config data.
    config = configparser.ConfigParser()
    config.read('main.conf')
    text_color = config['aesthetic']['text_color']
    text_area_height = config['aesthetic']['text_area_height']

    # Pull in install server list from game_servers.json file.
    install_list = get_servers()
    if not install_list:
        flash('Error loading game_servers.json file!', category='error')
        return redirect(url_for('views.home'))

    # Initialize blank install_name, used for update-text-area.js.
    install_name = ""

    # Kill any lingering background watch processes if page is reloaded.
    kill_watchers(last_request_for_output)

    # Bootstrap spinner colors.
    bs_colors = ['primary', 'secondary', 'success', 'danger', 'warning', \
                                                        'info', 'light']
    # Check for / install the main linuxgsm.sh script.
    lgsmsh = "linuxgsm.sh"
    check_and_get_lgsmsh(f"./scripts/{lgsmsh}")

    # Post logic only triggered after install form submission.
    if request.method == 'POST':
        server_script_name = request.form.get("server_name")
        server_full_name = request.form.get("full_name")
        sudo_pass = request.form.get("sudo_pass")

        # Make sure required options are supplied.
        for required_form_item in (server_script_name, server_full_name, sudo_pass):
            if required_form_item == None:
                flash("Missing Required Form Feild!", category="error")
                return redirect(url_for('views.install'))

            # Check input lengths.
            if len(required_form_item) > 150:
                flash("Form field too long!", category='error')
                return redirect(url_for('views.install'))

        # Validate form submission data against install list in json file.
        if install_options_are_invalid(server_script_name, server_full_name):
            flash("Invalid Installation Option(s)!", category="error")
            return redirect(url_for('views.install'))

        # Make server_full_name a unix friendly directory name.
        server_full_name = server_full_name.replace(" ", "_")
        server_full_name = server_full_name.replace(":", "_")

        # Used to pass install_name to frontend js.
        install_name = server_full_name

        # Object to hold output from any running daemon threads.
        output_obj = OutputContainer([''], False)

        # If this is the first time we're ever seeing the server_name then put it
        # and its associated output_obj in the global INSTALL_SERVERS dictionary.
        if not server_full_name in INSTALL_SERVERS:
            INSTALL_SERVERS[server_full_name] = output_obj

        # Set the output object to the one stored in the global dictionary.
        output = INSTALL_SERVERS[server_full_name]

        install_exists = GameServer.query.filter_by(install_name=server_full_name).first()

        if install_exists:
            flash('An installation by that name already exits.', category='error')
            return redirect(url_for('views.install'))

        if os.path.exists(server_full_name):
            flash('Install directory already exists.', category='error')
            flash('Did you perhaps have this server installed previously?', \
                                                            category='error')
            return redirect(url_for('views.install'))

        if not get_tty_ticket(sudo_pass):
            flash('Problem with sudo password!', category='error')
            return redirect(url_for('views.install'))

        # Make a new server dir and copy linuxgsm.sh into it.
        os.mkdir(server_full_name)
        shutil.copy(f"scripts/{lgsmsh}", server_full_name)

        install_path = os.getcwd() + '/' + server_full_name

        # Add the install to the database.
        new_game_server = GameServer(install_name=server_full_name, \
                install_path=install_path, script_name=server_script_name, \
                username=getpass.getuser())
        db.session.add(new_game_server)
        db.session.commit()

        cmd = [f'./{lgsmsh}', server_script_name]
        proc = subprocess.run(cmd, cwd=install_path, capture_output=True, text=True)

        if proc.returncode != 0:
            output.output_lines.append(proc.stderr)
        output.output_lines.append(proc.stdout)

        cmd = [f'./{server_script_name}', 'auto-install']
        install_daemon = Thread(target=shell_exec, args=(install_path, cmd, \
                                output), daemon=True, name='Install')
        install_daemon.start()

    return render_template("install.html", user=current_user, \
            servers=install_list, text_color=text_color, bs_colors=bs_colors, \
            install_name=install_name, text_area_height=text_area_height)


######### API System Usage #########
@views.route("/api/system-usage", methods=['GET'])
@login_required
def get_stats():
    server_stats = get_server_stats()
    response = Response(json.dumps(server_stats, indent=4), status=200, mimetype='application/json')
    return response


######### API CMD Output Page #########

@views.route("/api/cmd-output", methods=['GET'])
@login_required
def no_output():
    # Collect args from GET request.
    server_name = request.args.get("server")

    # Can't load the controls page without a server specified.
    if server_name == None:
        return """{ "error" : "eer can't load page n'@" }"""

    # Can't do anyting if we don't recognize the server_name.
    if server_name not in GAME_SERVERS and server_name not in INSTALL_SERVERS:
        return """{ "error" : "eer never heard of em" }"""

    # Reset the last requested output time.
    last_request_for_output = int(time.time())

    # If its a server in the INSTALL_SERVERS dict set the output object to the
    # one from that dictionary.
    if server_name in INSTALL_SERVERS:
        output = INSTALL_SERVERS[server_name]

    # If its a server in the GAME_SERVERS dict set the output object to the one
    # from that dictionary. Will clober the above after server is installed. Is
    # intentional.
    if server_name in GAME_SERVERS:
        output = GAME_SERVERS[server_name]

    # Returns json for used by ajax code on /controls route.
    return output.toJSON()


######### Settings Page #########

@views.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    # Kill any lingering background watch processes in case console page is
    # clicked away fromleft.
    kill_watchers(last_request_for_output)

    # Import config data.
    config = configparser.ConfigParser()
    config.read('main.conf')
    text_color = config['aesthetic']['text_color']
    text_area_height = config['aesthetic']['text_area_height']
    remove_files = config['settings'].getboolean('remove_files')
    graphs_primary = config['aesthetic']['graphs_primary']
    graphs_secondary = config['aesthetic']['graphs_secondary']
    show_stats = config['aesthetic'].getboolean('show_stats')

    config_options = {
        "text_color": text_color,
        "text_area_height": text_area_height,
        "remove_files": remove_files,
        "graphs_primary": graphs_primary,
        "graphs_secondary": graphs_secondary,
        "show_stats": show_stats
    }

    if request.method == 'GET':
        return render_template("settings.html", user=current_user, \
                                    config_options=config_options)

    text_color_pref = request.form.get("text_color")
    file_pref = request.form.get("delete_files")
    height_pref = request.form.get("text_area_height")
    purge_socks = request.form.get("purge_socks")
    update_weblgsm = request.form.get("update_weblgsm")
    graphs_primary_pref = request.form.get("graphs_primary")
    graphs_secondary_pref = request.form.get("graphs_secondary")
    show_stats_pref = request.form.get("show_stats")

    # Purge user's tmux socket files.
    if purge_socks:
        purge_user_tmux_sockets()

    # Set Remove files setting.
    config['settings']['remove_files'] = 'yes'
    if file_pref == "false":
        config['settings']['remove_files'] = 'no'

    # Text color settings.
    def valid_color(color):
        # Validate color code with regular expression.
        if re.search('^#(?:[0-9a-fA-F]{1,2}){3}$', color):
            return True

        return False

    if text_color_pref:
        if not valid_color(text_color_pref):
            flash('Invalid text color!', category='error')
            return redirect(url_for('views.settings'))
        config['aesthetic']['text_color'] = text_color_pref

    if graphs_primary_pref:
        if not valid_color(graphs_primary_pref):
            flash('Invalid primary color!', category='error')
            return redirect(url_for('views.settings'))
        config['aesthetic']['graphs_primary'] = graphs_primary_pref

    if graphs_secondary_pref:
        if not valid_color(graphs_secondary_pref):
            flash('Invalid secondary color!', category='error')
            return redirect(url_for('views.settings'))
        config['aesthetic']['graphs_secondary'] = graphs_secondary_pref

    # Default to no, if checkbox is unchecked.
    config['aesthetic']['show_stats'] = 'no'
    if show_stats_pref == 'true':
        config['aesthetic']['show_stats'] = 'yes'

    # Set default text area height setting.
    config['aesthetic']['text_area_height'] = text_area_height
    if height_pref:
        # Validate textarea height is int.
        try:
            height_pref = int(height_pref)
        except ValueError:
            flash('Invalid Textarea Height!', category='error')
            return redirect(url_for('views.settings'))

        # Check if height pref is in valid range.
        if height_pref > 100 or height_pref < 5:
            flash('Invalid Textarea Height!', category='error')
            return redirect(url_for('views.settings'))

        # Have to cast back to string to save in config.
        config['aesthetic']['text_area_height'] = str(height_pref)

    with open('main.conf', 'w') as configfile:
         config.write(configfile)

    # Update's the weblgsm.
    if update_weblgsm:
        status = update_self()
        flash("Settings Updated!")
        if 'Error:' in status:
            flash(status, category='error')
            return redirect(url_for('views.settings'))

        flash(status)

        # Restart daemon thread sleeps for 5 seconds then restarts app.
        cmd = ['./web-lgsm.py', '--restart']
        restart_daemon = Thread(target=restart_self, args=(cmd,), 
                                    daemon=True, name='restart')
        restart_daemon.start()
        return redirect(url_for('views.settings'))

    flash("Settings Updated!")
    return redirect(url_for('views.settings'))


######### About Page #########

@views.route("/about", methods=['GET'])
@login_required
def about():
    # Kill any lingering background watch processes.
    # In case console page is clicked away from.
    kill_watchers(last_request_for_output)

    # Import config data.
    config = configparser.ConfigParser()
    config.read('main.conf')
    text_color = config['aesthetic']['text_color']

    return render_template("about.html", user=current_user, \
                                        text_color=text_color)


######### Add Page #########

@views.route("/add", methods=['GET', 'POST'])
@login_required
def add():
    # Import config data.
    config = configparser.ConfigParser()
    config.read('main.conf')
    remove_files = config['settings'].getboolean('remove_files')

    # Kill any lingering background watch processes in case console page is
    # clicked away fromleft.
    kill_watchers(last_request_for_output)

    # Set default status_code.
    status_code = 200

    if request.method == 'POST':
        install_name = request.form.get("install_name")
        install_path = request.form.get("install_path")
        script_name = request.form.get("script_name")
        username = request.form.get("username")

        # Check all required args are submitted.
        for required_form_item in (install_name, install_path, script_name):
            if required_form_item == None or required_form_item == '':
                flash("Missing required form field(s)!", category="error")
                return redirect(url_for('views.add'))

            # Check input lengths.
            if len(required_form_item) > 150:
                flash("Form field too long!", category='error')
                return redirect(url_for('views.add'))

        system_user = getpass.getuser()
        # Set default user if none provided.
        if username == None or username == '':
            username = system_user

        if len(username) > 150:
            flash("Form field too long!", category='error')
            return redirect(url_for('views.add'))

        # Returns None if invalid username.
        if get_uid(username) == None:
            flash("User not found on system!", category='error')
            return redirect(url_for('views.add'))

        # Make install name unix friendly for dir creation.
        install_name = install_name.replace(" ", "_")
        install_name = install_name.replace(":", "_")

        install_exists = GameServer.query.filter_by(install_name=install_name).first()

        # Try to prevent arbitrary bad input.
        for input_item in (install_name, install_path, script_name, username):
            if contains_bad_chars(input_item):
                flash("Illegal Character Entered!", category="error")
                flash(r"""Bad Chars: $ ' " \ # = [ ] ! < > | ; { } ( ) * , ? ~ &""", \
                                                            category="error")
                return redirect(url_for('views.add'))

        if install_exists:
            flash('An installation by that name already exits.', category='error')
            status_code = 400

        elif not os.path.exists(install_path) or not os.path.isdir(install_path):
            flash('Directory path does not exist.', category='error')
            status_code = 400

        elif script_name_is_invalid(script_name):
            flash('Invalid game server script file name!', category='error')
            status_code = 400

        elif not os.path.exists(install_path + '/' + script_name) or \
                not os.path.isfile(install_path + '/' + script_name):
            flash('Script file does not exist.', category='error')
            status_code = 400

        else:
            # Add the install to the database, then redirect home.
            new_game_server = GameServer(install_name=install_name, \
                        install_path=install_path, script_name=script_name, \
                        username=username)
            db.session.add(new_game_server)
            db.session.commit()

            flash('Game server added!')
            if username != system_user:
                flash(f'''
                    NOTE: You will need to add a sudoers rule like the following in
                    order for game servers owned by other users to function
                    properly. You can edit your sudoers file using: "sudo visudo".
                    Add this line: 
                    {system_user} ALL=({username}) NOPASSWD: {install_path}/{script_name}, /usr/bin/watch, /usr/bin/tmux, /usr/bin/kill
                ''')
            return redirect(url_for('views.home'))

    return render_template("add.html", user=current_user), status_code


######### Delete Route #########

@views.route("/delete", methods=['GET', 'POST'])
@login_required
def delete():
    # Import config data.
    config = configparser.ConfigParser()
    config.read('main.conf')
    remove_files = config['settings'].getboolean('remove_files')

    # Delete via POST is for multiple deletions.
    # Post submissions come from delete toggles on home page.
    if request.method == 'POST':
        for server_id, server_name in request.form.items():
            server = GameServer.query.filter_by(install_name=server_name).first()
            if server:
                del_server(server, remove_files)
    else:
        server_name = request.args.get("server")
        if server_name == None:
            flash("Missing Required Args!", category="error")
            return redirect(url_for('views.home'))

        server = GameServer.query.filter_by(install_name=server_name).first()
        if server:
            del_server(server, remove_files)

    return redirect(url_for('views.home'))


######### Edit Route #########
@views.route("/edit", methods=['GET', 'POST'])
@login_required
def edit():
    # The abbreviation cfg will be used to refer to any lgsm game server
    # specific config files. Whereas, the word config will be used to refer to
    # any web-lgsm config info.

    # Import config data.
    config = configparser.ConfigParser()
    config.read('main.conf')
    text_color = config['aesthetic']['text_color']
    text_area_height = config['aesthetic']['text_area_height']

    if config['settings']['cfg_editor'] == 'no':
        flash("Config Editor Disabled", category="error")
        return redirect(url_for('views.home'))

    # Collect args from POST request.
    server_name = request.form.get("server")
    cfg_path = request.form.get("cfg_path")
    new_file_contents = request.form.get("file_contents")
    download = request.form.get("download")

    # Can't load the edit page without a server specified.
    if server_name == None or server_name == "":
        flash("No server specified!", category="error")
        return redirect(url_for('views.home'))

    # Can't load the edit page without a cfg specified.
    if cfg_path == None or cfg_path == "":
        flash("No config file specified!", category="error")
        return redirect(url_for('views.home'))

    # Check that the submitted server exists in db.
    server = GameServer.query.filter_by(install_name=server_name).first()
    # If game server doesn't exist in db, can't load page for it.
    if server == None:
        flash("Invalid game server name!", category="error")
        return redirect(url_for('views.home'))

    # Checks that install dir exists.
    if not os.path.isdir(server.install_path):
        flash("No game server installation directory found!", category="error")
        return redirect(url_for('views.home'))

    # Try to pull script's basename from supplied cfg_path.
    try:
        cfg_file = os.path.basename(cfg_path)
    except:
        flash("Error getting config file basename!", category="error")
        return redirect(url_for('views.home'))

    # Validate cfg_file name is in list of accepted cfgs.
    if is_invalid_cfg_name(cfg_file):
        flash("Invalid config file name!", category="error")
        return redirect(url_for('views.home'))

    # Check that file exists before allowing writes to it. Aka don't allow
    # arbitrary file creation. Even though the above should block creating
    # files with arbitrary names, we still don't want to allow arbitrary file
    # creation anywhere on the file system the app has write perms to.
    if not os.path.isfile(cfg_path):
        flash("No such file!", category="error")
        return redirect(url_for('views.home'))

    # If new_file_contents supplied in post request, write the new file
    # contents to the cfg file.
    if new_file_contents:
        try:
            with open(cfg_path, 'w') as f:
                f.write(new_file_contents.replace('\r', ''))
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
        return redirect(url_for('views.home'))

    # If is download request.
    if download == "yes":
        basedir, basename = os.path.split(cfg_path)
        return send_from_directory(basedir, basename, as_attachment=True)

    return render_template("edit.html", user=current_user, \
    text_color=text_color, text_area_height=text_area_height, \
                server_name=server_name, cfg_file=cfg_path, \
                file_contents=file_contents, cfg_file_name=cfg_file)

