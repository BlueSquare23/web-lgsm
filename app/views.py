import os
import re
import sys
import json
import shutil
import subprocess
import configparser
from . import db
from .utils import *
from .models import *
from threading import Thread
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, flash, url_for, \
                                                    redirect, Response

# Global object to hold output from any running daemon threads.
output = OutputContainer([], False, False)

# Initialize view blueprint.
views = Blueprint("views", __name__)


######### Home Page #########

@views.route("/", methods=['GET'])
@views.route("/home", methods=['GET'])
@login_required
def home():
    # Import meta data.
    meta_data = db.session.get(MetaData, 1)
    base_dir = meta_data.app_install_path

    # Import config data.
    config = configparser.ConfigParser()
    config.read(f'{base_dir}/main.conf')

    servers = GameServer.query.all()
    server_names = []

    for server in servers:
        server_names.append(server.install_name)

    return render_template("home.html", user=current_user, \
                                installed_servers=server_names)


######### Controls Page #########

@views.route("/controls", methods=['GET'])
@login_required
def controls():
    # Import meta data.
    meta_data = db.session.get(MetaData, 1)
    base_dir = meta_data.app_install_path

    # Import config data.
    config = configparser.ConfigParser()
    config.read(f'{base_dir}/main.conf')
    text_color = config['aesthetic']['text_color']

    # Bootstrap spinner colors.
    bs_colors = ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light']

    # Collect args from GET request.
    server_name = request.args.get("server")
    script_arg = request.args.get("command")

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

    script_path = server.install_path + '/' + server.script_name

    # This code block is only triggered in the event the script_arg param is
    # supplied with the GET request. Aka if a user has clicked one of the
    # control button.
    if script_arg != None:
        # Validate script_arg against contents of commands.json file.
        if is_invalid_command(script_arg):
            flash("Invalid Command!", category="error")
            return redirect(url_for('views.controls', server=server_name))

        # Console option, use tmux capture-pane to get output.
        if script_arg == "c":
            # First check if tmux session is running.
            cmd = f'/usr/bin/tmux has-session -t {server.script_name}'
            proc = subprocess.Popen(cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            stdout, stderr = proc.communicate()

            # Return any errors checking tmux session.
            if len(stderr) > 0:
                # Clear any previous output.
                output.output_lines.clear()
                output.output_lines.append(stderr.decode())

                flash("No Console Output!", category='error')
                return redirect(url_for('views.controls', server=server_name))

            # Otherwise, use the `watch` command to keep live console running.
            cmd = f'/usr/bin/watch -te /usr/bin/tmux capture-pane -pt {server.script_name}'
            daemon = Thread(target=shell_exec, args=(server.install_path, cmd, \
                                    output), daemon=True, name='Console')
            daemon.start()
            flash("Console Started!")
            return redirect(url_for('views.controls', server=server_name))

        # If its not the console command
        else:
            cmd = f'{script_path} {script_arg}'
            daemon = Thread(target=shell_exec, args=(server.install_path, cmd, \
                                    output), daemon=True, name='Command')
            daemon.start()
            return redirect(url_for('views.controls', server=server_name))

    # Default to no refresh.
    refresh = False

    # If the process is still running or just finished running do a refresh.
    if output.process_lock or output.just_finished:
        refresh = True
        print("#### Do a refresh!")
        output.just_finished = False

    return render_template("controls.html", user=current_user, \
        server_name=server_name, server_commands=get_commands(), \
        text_color=text_color, bs_colors=bs_colors, refresh=refresh)

######### Output Page #########

@views.route("/output", methods=['GET'])
@login_required
def no_output():

    # Convert & return json using .toJSON() method.
    return output.toJSON()

    # Renders output page with latest content from output object.
    # Used for Ajax requests to populate /controls output textarea.
    #return render_template("output.html", output=output)


########## Iframe Default Page #########
#
#@views.route("/no_output", methods=['GET'])
#@login_required
#def no_output():
#    # Import meta data.
#    meta_data = db.session.get(MetaData, 1)
#    base_dir = meta_data.app_install_path
#
#    # Import config data.
#    config = configparser.ConfigParser()
#    config.read(f'{base_dir}/main.conf')
#    text_color = config['aesthetic']['text_color']
#
#    return render_template("no_output.html", text_color=text_color)


######### Install Page #########

@views.route("/install", methods=['GET', 'POST'])
@login_required
def install():
    # Import meta data.
    meta_data = db.session.get(MetaData, 1)
    base_dir = meta_data.app_install_path

    # Import config data.
    config = configparser.ConfigParser()
    config.read(f'{base_dir}/main.conf')
    text_color = config['aesthetic']['text_color']

    ## Make its own function / find better solution.
    # Check for / install the main linuxgsm.sh script.
    lgsmsh = "linuxgsm.sh"
    check_and_get_lgsmsh(f"{base_dir}/{lgsmsh}")

    if request.method == 'POST':
        server_script_name = request.form.get("server_name")
        server_full_name = request.form.get("full_name")
        sudo_pass = request.form.get("sudo_pass")

        # Make sure required options are supplied.
        for item in (server_script_name, server_full_name, sudo_pass):
            if item == None:
                flash("Missing Required Form Feild!", category="error")
                return redirect(url_for('views.install'))

        # Validate form submission data against install list in json file.
        if install_options_are_invalid(server_script_name, server_full_name):
            flash("Invalid Installation Option(s)!", category="error")
            return redirect(url_for('views.install'))

        # Make server_full_name a unix friendly directory name.
        server_full_name = server_full_name.replace(" ", "_")

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

        # Make a new server dir and copy linuxgsm.sh into it then cd into it.
        os.mkdir(server_full_name)
        shutil.copy(lgsmsh, server_full_name)

        install_path = base_dir + '/' + server_full_name

        # Add the install to the database.
        new_game_server = GameServer(install_name=server_full_name, \
                install_path=install_path, script_name=server_script_name)
        db.session.add(new_game_server)
        db.session.commit()

        cmd = f'./{lgsmsh} {server_script_name} ; ./{server_script_name} ai'

        # Only flashes after install redirect to home page.
        flash("Game server added!")

        daemon = Thread(target=shell_exec, args=(server.install_path, cmd, \
                                output), daemon=True, name='Command')
        daemon.start()
#        return Response(read_process(install_path, base_dir, setup_cmd, \
#                        text_color, "install"), mimetype= 'text/html')

    # If the process is still running or just finished running do a refresh.
    if output.process_lock == True or output.just_finished == True:
        refresh = True
        print("#### Do a refresh!")
        output.just_finished = False

    return render_template("install.html", user=current_user, \
    servers=get_servers(), text_color=text_color, output=output)


######### Settings Page #########

@views.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    # Import meta data.
    meta_data = db.session.get(MetaData, 1)
    base_dir = meta_data.app_install_path

    # Import config data.
    config = configparser.ConfigParser()
    config.read(f'{base_dir}/main.conf')
    text_color = config['aesthetic']['text_color']
    remove_files = config['settings'].getboolean('remove_files')

    if request.method == 'POST':
        color_pref = request.form.get("text_color")
        file_pref = request.form.get("delete_files")

        config['settings']['remove_files'] = 'yes'
        if file_pref == "false":
            config['settings']['remove_files'] = 'no'

        config['aesthetic']['text_color'] = text_color
        if color_pref != None:
            # Validate color code with regular expression.
            if not re.search('^#(?:[0-9a-fA-F]{1,2}){3}$', color_pref):
                flash('Invalid color!', category='error')
                return redirect(url_for('views.settings'))

            config['aesthetic']['text_color'] = color_pref

        with open(f'{base_dir}/main.conf', 'w') as configfile:
             config.write(configfile)

        flash("Settings Updated!")
        return redirect(url_for('views.settings'))

    return render_template("settings.html", user=current_user, \
                text_color=text_color, remove_files=remove_files)


######### Add Page #########

@views.route("/add", methods=['GET', 'POST'])
@login_required
def add():
    # Import meta data.
    meta_data = db.session.get(MetaData, 1)
    base_dir = meta_data.app_install_path

    # Import config data.
    config = configparser.ConfigParser()
    config.read(f'{base_dir}/main.conf')
    remove_files = config['settings'].getboolean('remove_files')

    # Set default status_code.
    status_code = 200

    if request.method == 'POST':
        install_name = request.form.get("install_name")
        install_path = request.form.get("install_path")
        script_name = request.form.get("script_name")

        # Check all required args are submitted.
        for required_form_item in (install_name, install_path, script_name):
            if required_form_item == None or required_form_item == '':
                flash("Missing required form field(s)!", category="error")
                return redirect(url_for('views.add'))

        # Make install name unix friendly for dir creation.
        install_name = install_name.replace(" ", "_")

        install_exists = GameServer.query.filter_by(install_name=install_name).first()

        # Try to prevent arbitrary bad input.
        for input_item in (install_name, install_path, script_name):
            if contains_bad_chars(input_item):
                flash("Illegal Character Entered!", category="error")
                flash(r"""Bad Chars: $ ' " \ # = [ ] ! < > | ; { } ( ) * , ? ~ &""", \
                                                            category="error")
                return redirect(url_for('views.add'))

        # Only allow lgsm installs under home dir.
        user_home_dir = os.path.expanduser('~')

        if install_exists:
            flash('An installation by that name already exits.', category='error')
            status_code = 400

        elif not os.path.exists(install_path) or not os.path.isdir(install_path):
            flash('Directory path does not exist.', category='error')
            status_code = 400

        elif os.path.commonprefix((os.path.realpath(install_path),user_home_dir)) != user_home_dir:
            flash(f'Only dirs under {user_home_dir} allowed!', category='error')
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
                        install_path=install_path, script_name=script_name)
            db.session.add(new_game_server)
            db.session.commit()

            flash('Game server added!')
            return redirect(url_for('views.home'))

    return render_template("add.html", user=current_user), status_code


# Does the actual deletions for the /delete route.
def del_server(server, remove_files):
    install_path = server.install_path
    server_name = server.install_name

    GameServer.query.filter_by(install_name=server_name).delete()
    db.session.commit()

    if remove_files:
        if os.path.isdir(install_path):
            shutil.rmtree(install_path)

    flash(f'Game server, {server_name} deleted!')
    return

######### Delete Route #########

@views.route("/delete", methods=['GET', 'POST'])
@login_required
def delete():
    # Import meta data.
    meta_data = db.session.get(MetaData, 1)
    base_dir = meta_data.app_install_path

    # Import config data.
    config = configparser.ConfigParser()
    config.read(f'{base_dir}/main.conf')
    remove_files = config['settings'].getboolean('remove_files')

    # Delete via POST is for multiple deletions, from toggles on home page.
    if request.method == 'POST':
        for server_id, server_name in request.form.items():
            server = GameServer.query.filter_by(install_name=server_name).first()
            if server != None:
                del_server(server, remove_files)
    else:
        server_name = request.args.get("server")
        if server_name == None:
            flash("Missing Required Args!", category=error)
            return redirect(url_for('views.home'))

        server = GameServer.query.filter_by(install_name=server_name).first()
        if server != None:
            del_server(server, remove_files)

    return redirect(url_for('views.home'))
