import os
import sys
import subprocess
import shutil
from flask import Blueprint, render_template, request, flash, url_for, redirect, Response
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .models import User, GameServer
from . import db
from .utils import *
#run_script, capture_tmux_pane, escape_ansi, get_doggo, \
#    contains_bad_chars, list_all_lgsm_servers, wget_lgsmsh, install_lgsm_server

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
    disabled_cmds = ['d', 'sk', 'i', 'dev']

    if script_arg != None:
        # Check for hax injectypoo attempt!
        if contains_bad_chars(script_arg):
            flash("Illegal Character Entered", category="error")
            flash("Bad Chars: $ ' \" \ # = [ ] ! < > | ; { } ( ) * , ? ~ &", category="error")
            return redirect(url_for('views.controls', server=server_name))

        # Not allowed to start in debug mode.
        if script_arg in disabled_cmds:
            flash("Option disabled", category="error")
            return redirect(url_for('views.controls', server=server_name))

        # If its live console use custom python console solution.
        if script_arg == "c":
            stdout, stderr = capture_tmux_pane(server.script_name)
            output = escape_ansi(stdout)
            output_type = "stdout"

            if stderr != "":
                output = escape_ansi(stderr)
                output_type = "stderr"
            

    stdout, stderr = rce(script_path, "")

    # For Debug.
    if stderr != "":
        print(stderr)

    cmds = escape_ansi(stdout)

    class CmdDescriptor:
        def __init__(self):
            self.long_cmd  = ""
            self.short_cmd = ""
            self.description = ""

    commands = []

    before_commands_line = True

    for line in cmds.splitlines():
        # We only care about lines after Commands line.
        if line.rstrip() == "Commands":
            before_commands_line = False
            continue

        if before_commands_line:
            continue

        cmd = CmdDescriptor()
        args = line.split()

        if args[1] in disabled_cmds:
            continue

        cmd.long_cmd = args[0]
        cmd.short_cmd = args[1]
        cmd.description = line.split("|")[1]
        commands.append(cmd)

    return render_template("controls.html", user=current_user, server_name=server_name, server_commands=commands, cmd=script_arg, doggo_img=get_doggo())

######### Console Page #########

@views.route("/rconsole", methods=['GET'])
@login_required
def rconsole():
    def execute(cmd):
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    def read_process(cmd_list):
        yield "<pre style='color:green'>"
        for line in execute(cmd_list):
            yield escape_ansi(line)
            #print(line, end="")
        yield "</pre>"

    server_name = request.args.get("server")
    script_arg = request.args.get("command")

    if script_arg == "None":
        return Response( "<h3 style='color:green'>No output currently!</h3>", mimetype = 'text/html' )

    server = GameServer.query.filter_by(install_name=server_name).first()
    script_path = server.install_path + '/' + server.script_name

    cmd_list = [script_path, script_arg]
    return Response(read_process(cmd_list), mimetype= 'text/html')

######### Install Page #########

@views.route("/install", methods=['GET', 'POST'])
@login_required
def install():
    output = ""

    # Check for / install the main linuxgsm.sh script. 
    lgsmsh = "linuxgsm.sh"
    if not os.path.isfile(lgsmsh):
        stdout, stderr = wget_lgsmsh()

        # For Debug.
        if stderr != "":
            print(stderr)

    os.chmod(lgsmsh, 0o755)

    if request.method == 'GET':
        server_script_name = request.args.get("server")
        server_full_name = request.args.get("full_name")

        if server_script_name != None and server_full_name != None:
            server_full_name = server_full_name.replace(" ", "_")
            # Gotta check all input, even if it should just be coming from buttons.
            for input_item in (server_script_name, server_full_name):
                if contains_bad_chars(input_item):
                    flash("Illegal Character Detected! Stop Haxing!", category="error")
                    return redirect(url_for('views.install'))

            install_name_exists = GameServer.query.filter_by(install_name=server_full_name).first()
            
            if install_name_exists:
                flash('An installation by that name already exits.', category='error')
                return redirect(url_for('views.install'))
            elif os.path.exists(server_full_name):
                flash('Install directory already exists.', category='error')
                flash('Did you perhaps have this server installed previously?', category='error')
                return redirect(url_for('views.install'))
            
            # Make a new server dir and copy linuxgsm.sh into it then cd into it.
            os.mkdir(server_full_name)
            shutil.copy(lgsmsh, server_full_name)
            os.chdir(server_full_name)

            # Add the install to the database.
            new_game_server = GameServer(install_name=server_full_name, install_path=server_full_name, script_name=server_script_name) 
            db.session.add(new_game_server)
            db.session.commit()

            try:
                stdout, stderr = pre_install_lgsm_server(server_script_name)
            except:
                # For debug.
                print(sys.exc_info()[0])

            # For Debug.
            if stderr != "":
                output = escape_ansi(stderr)
        
            output = escape_ansi(stdout)

            print(os.getcwd())
            os.chdir('..')

            # Wont flash till install finishes.
            flash('Game server added to Web LGSM DB!')
            flash('Game server sucessfully installed!')

            # Redirect to the auto controls page and run the auto install (ai) command.
            return redirect(url_for('views.controls', server=server_full_name, command='ai'))

    # Run linuxgsm.sh to get dictionary listing of servers to install.
    stdout, stderr = list_all_lgsm_servers()
    
    # For Debug.
    if stderr != "":
        print(stderr)

    servers_list = escape_ansi(stdout)
    servers = {}
    
    for line in servers_list.splitlines():
        server_script_name = line.split()[0]
        server_full_name = line.split(" ", 1)[1].strip()

        # Part of status stdout, not part of listing so ignore.
        if server_script_name == "fetching":
            continue

        servers[server_script_name] = server_full_name

    return render_template("install.html", user=current_user, servers=servers, output=output, doggo_img=get_doggo())

######### Settings Page #########

@views.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    
    return render_template("settings.html", user=current_user)

######### Add Page #########

@views.route("/add", methods=['GET', 'POST'])
@login_required
def add():

    if request.method == 'POST':
        install_name = request.form.get("install_name").replace(" ", "_")
        install_path = request.form.get("install_path")
        script_name = request.form.get("script_name")

        install_name_exists = GameServer.query.filter_by(install_name=install_name).first()

        for input_item in (install_name, install_path, script_name):
            if contains_bad_chars(input_item):
                flash("Illegal Character Entered", category="error")
                flash("Bad Chars: $ ' \" \ # = [ ] ! < > | ; { } ( ) * , ? ~ &", category="error")
                return redirect(url_for('views.add'))

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

# Helper function for del route.
def del_server(server_name):
    GameServer.query.filter_by(install_name=server_name).delete()
    db.session.commit()

    if os.path.isdir(server_name):
        shutil.rmtree(server_name)
    
    flash(f'Game server, {server_name} deleted!')
    return

######### Delete Route #########

@views.route("/delete", methods=['GET', 'POST'])
@login_required
def delete():
    # For multiple deletions from home page.
    if request.method == 'POST':
        for server, server_name in request.form.items():
            # Always check all input!
            if contains_bad_chars(server) or contains_bad_chars(server_name):
                flash("Illegal Character Detected! Stop Haxing!", category="error")
                return redirect(url_for('views.home'))
            del_server(server_name)
    else:
        server_name = request.args.get("server")
        # Always check all input!
        if contains_bad_chars(server_name):
            flash("Illegal Character Detected! Stop Haxing!", category="error")
            return redirect(url_for('views.home'))
        del_server(server_name)

    return redirect(url_for('views.home'))
