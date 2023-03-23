import os
from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .models import User, GameServer
from . import db
from .utils import run_script, escape_ansi, check_input, get_doggo

views = Blueprint("views", __name__)

######### Home Page #########

@views.route("/", methods=['GET'])
@views.route("/home", methods=['GET'])
@login_required
def home():
    servers = GameServer.query.all()
    server_names = []

    for server in servers:
        server_names.append(server.install_name)

    return render_template("home.html", user=current_user, installed_servers=server_names)

######### Controls Page #########

@views.route("/controls", methods=['GET'])
@login_required
def controls():

    server_name = request.args.get("server")
    script_arg = request.args.get("command")

    if server_name == None:
        flash("Error loading page", category="error")
        return redirect(url_for('views.home'))

    server = GameServer.query.filter_by(install_name=server_name).first()
    script_path = server.install_path + '/' + server.script_name
    output = ""
    output_type = ""

    if script_arg != None:
        # Check for hax injectypoo attempt!
        check_input(script_arg)

        # If arg is install, deny (requires stdin (y/n) prompts).
        if script_arg == "i":
            flash("Install option disabled", category="error")
            return redirect(url_for('views.controls', server_name=server_name))

        # Not allowed to start in debug mode.
        if script_arg == "d":
            flash("Debug option disabled", category="error")
            return redirect(url_for('views.controls', server_name=server_name))

        # Not allowed to create a skel dir.
        if script_arg == "sk":
            flash("Skel dir option disabled", category="error")
            return redirect(url_for('views.controls', server_name=server_name))

        # If its live console use custom python console solution.
        if script_arg == "c":
            stdout, stderr = capture_tmux_pane()
            output = escape_ansi(stdout)
            output_type = "stdout"

            if stderr != "":
                output = escape_ansi(stderr)
                output_type = "stderr"

        stdout, stderr = run_script(script_path, script_arg)

        # For Debug.
        if stderr != "":
            output = escape_ansi(stderr)
            output_type = "stderr"

        output = escape_ansi(stdout)
        output_type = "stdout"

#        output, output_type = process_script_args(script_path, script_arg, server_name)

    stdout, stderr = run_script(script_path, "")

    # For Debug.
    if stderr != "":
        print(stderr)

    # Drop first 6 lines of useless output.
    cmds = escape_ansi(stdout).split('\n',6)[-1]

    class CmdDescriptor:
        def __init__(self):
            self.long_cmd  = ""
            self.short_cmd = ""
            self.description = ""

    commands = []

    for line in cmds.splitlines():
        cmd = CmdDescriptor()
        args = line.split()
        cmd.long_cmd = args[0]
        cmd.short_cmd = args[1]
        cmd.description = line.split("|")[1]
        commands.append(cmd)

    return render_template("controls.html", user=current_user, \
    server_name=server_name, server_commands=commands, output=output, \
    output_type=output_type, doggo_img=get_doggo())


######### Install Page #########

@views.route("/install", methods=['GET'])
@login_required
def install():
    return render_template("install.html", user=current_user)

######### Add Page #########

@views.route("/add", methods=['GET', 'POST'])
@login_required
def add():

    if request.method == 'POST':
        install_name = request.form.get("install_name")
        install_path = request.form.get("install_path")
        script_name = request.form.get("script_name")

        install_name_exists = GameServer.query.filter_by(install_name=install_name).first()

        if install_name_exists:
            flash('An installation by that name already exits.', category='error')
        elif not os.path.exists(install_path) or not os.path.isdir(install_path):
            flash('Directory path does not exist.', category='error')
        elif not os.path.exists(install_path + '/' + script_name) or \
                not os.path.isfile(install_path + '/' + script_name):
            flash('Script file does not exist.', category='error')
        else:
            # Add the install to the database, then redirect home.
            new_game_server = GameServer(install_name=install_name, install_path=install_path, script_name=script_name) 
            db.session.add(new_game_server)
            db.session.commit()

            flash('Game server added!')
            return redirect(url_for('views.home'))
    
    return render_template("add.html", user=current_user)


######### Delete Route #########

@views.route("/delete", methods=['GET', 'POST'])
@login_required
def delete():

    return render_template("delete.html", user=current_user)
