import os
import sys
import subprocess
import shutil
from flask import Blueprint, render_template, request, flash, url_for, redirect, Response
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .models import *
from . import db
from .utils import *

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


# Controls route helper function. Uses script_path to gather list of short &
# long cmds and then commits them to the db. Helps speed up page load times if
# cmds are pulled from db rather than gathered each time via a popen call.
def add_cmd_to_db(server_name, script_path, disabled_cmds):

    # Requires further validation!!!
    ## TRY TO VALIDATE EVERYTHING!!!
    try:
        stdout = os.popen(script_path).read()
    except:
        # For debug.
        print(sys.exc_info()[0])

    cmds = escape_ansi(stdout)

    long_cmds = []
    short_cmds = []
    descriptions = []

    before_commands_line = True

    for line in cmds.splitlines():
        # Only the command lines have a | char.
        if "|" not in line:
            continue

        args = line.split()

        if args[1] in disabled_cmds:
            continue

        long_cmds.append(args[0])
        short_cmds.append(args[1])
        descriptions.append(line.split("|")[1])

    controls = ControlSet(install_name=server_name, short_cmds=','.join(short_cmds), \
                 long_cmds=','.join(long_cmds), descriptions=','.join(descriptions)) 
    db.session.add(controls)
    db.session.commit()
    return controls

# Parse /controls route GET/POST args input.
def controls_arg_parse(script_arg, script_path, sudo_pass, disabled_cmds):
    if script_arg in disabled_cmds:
        flash("Option disabled", category="error")
        return redirect(url_for('views.controls', server=server_name))

    # Auto install option, requires sudo pass to install any lgsm dependancies.
    if script_arg == "ai":
        if sudo_pass == None:
            flash("Auto install option requires sudo password!", category="error")
            return redirect(url_for('views.controls', server=server_name))

        escaped_password = sudo_pass.replace('"', '\\"')

        # Attempt's to get sudo tty ticket.
        try:
            print(os.popen(f'/usr/bin/echo "{escaped_password}" | /usr/bin/sudo -S apt-get check').read())
        except:
            # For debug.
            print(sys.exc_info()[0])

        cmd_list = [script_path, script_arg]
        return Response(read_process(server.install_path, base_dir, cmd_list), mimetype= 'text/html')

    # Console option, use tmux capture-pane.
    elif script_arg == "c":
        cmd_list = ['/usr/bin/tmux', 'capture-pane', '-pS', '-5', '-t', server.script_name]
        return Response(read_process(server.install_path, base_dir, cmd_list), mimetype= 'text/html')
    else:
        cmd_list = [script_path, script_arg]
        return Response(read_process(server.install_path, base_dir, cmd_list), mimetype= 'text/html')

######### Controls Page #########

@views.route("/controls", methods=['GET', 'POST'])
@login_required
def controls():
    # Import meta data.
    meta_data = MetaData.query.get(1)
    base_dir = meta_data.app_install_path
    # For GET->POST proxy.
    auto_post = False

    print(os.getcwd())
    if request.method == 'POST':
        server_name = request.form.get("server")
        script_arg = request.form.get("command")
        # Only needed for auto install command.
        sudo_pass = request.form.get("sudo_pass")
    else:
        server_name = request.args.get("server")
        script_arg = request.args.get("command")

    if server_name == None:
        flash("Error, no server specified!", category="error")
        return redirect(url_for('views.home'))

    server = GameServer.query.filter_by(install_name=server_name).first()
    if server == None:
        flash("Error loading page!", category="error")
        return redirect(url_for('views.home'))

    script_path = server.install_path + '/' + server.script_name
    disabled_cmds = ['d', 'sk', 'i', 'dev']

    controls = ControlSet.query.filter_by(install_name=server_name).first()
    if controls == None:
        controls = add_cmd_to_db(server_name, script_path, disabled_cmds)

    class CmdDescriptor:
        def __init__(self):
            self.long_cmd  = ""
            self.short_cmd = ""
            self.description = ""

    commands = []
    cmd_strings = zip(controls.short_cmds.split(','), controls.long_cmds.split(','), \
                                                controls.descriptions.split(','))

    for short_cmd, long_cmd, description in cmd_strings:
        cmd = CmdDescriptor()
        cmd.long_cmd = long_cmd
        cmd.short_cmd = short_cmd
        cmd.description = description
        commands.append(cmd)

    # Check for hax injectypoo attempt!
    for input_item in (server_name, script_arg):
        if contains_bad_chars(input_item):
            flash("Illegal Character Entered", category="error")
            flash("Bad Chars: $ ' \" \ # = [ ] ! < > | ; { } ( ) * , ? ~ &", category="error")
            return redirect(url_for('views.controls', server=server_name))

    if script_arg != None:
        if request.method == 'POST':
            controls_arg_parse(script_arg, script_path, sudo_pass, disabled_cmds)
        else:
            auto_post = True
       
    return render_template("controls.html", user=current_user, server_name=server_name, \
        server_commands=commands, cmd=script_arg, doggo_img=get_doggo(), auto_post=auto_post)

######### Iframe Default Page #########

@views.route("/no_output", methods=['GET'])
@login_required
def no_output():
    return render_template("no_output.html", user=current_user)

# Install route helper function. Uses the main linuxgsm.sh to gather list of
# short & long server names and then commits them to the db. Helps speed up
# page load times if server names are pulled from db rather than gathered each
# time via a popen call.
def add_server_list_to_db():
    try:
        stdout = os.popen('./linuxgsm.sh list').read()
    except:
        # For debug.
        print(sys.exc_info()[0])

    servers_list = escape_ansi(stdout)
    short_server_names = []
    long_server_names = []

    for line in servers_list.splitlines():
        server_script_name = line.split()[0]
        server_full_name = line.split(" ", 1)[1].strip()

        # Part of status stdout, not part of listing so ignore.
        if server_script_name == "fetching":
            continue

        short_server_names.append(server_script_name)
        long_server_names.append(server_full_name)

    servers = InstallServer(short_names=','.join(short_server_names), \
                            long_names=','.join(long_server_names))
    db.session.add(servers)
    db.session.commit()
    return servers

######### Install Page #########

@views.route("/install", methods=['GET'])
@login_required
def install():
    # Import meta data.
    meta_data = MetaData.query.get(1)
    base_dir = meta_data.app_install_path
    output = ""

    # Check for / install the main linuxgsm.sh script. 
    lgsmsh = "linuxgsm.sh"
    if not os.path.isfile(lgsmsh):
        # Temporary solution. Tried using requests for download, didn't work.
        try:
            os.popen("/usr/bin/wget -O linuxgsm.sh https://linuxgsm.sh")
        except:
            # For debug.
            print(sys.exc_info()[0])

    os.chmod(lgsmsh, 0o755)

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

        install_path = base_dir + '/' + server_full_name

        # Add the install to the database.
        new_game_server = GameServer(install_name=server_full_name, \
                install_path=install_path, script_name=server_script_name) 
        db.session.add(new_game_server)
        db.session.commit()
        
        setup_cmd = [f'./{lgsmsh}', server_script_name]

        flash("Game server added to database!")
        flash("Please enter sudo password to auto install the game server!")

        return Response(read_process(install_path, base_dir, setup_cmd), mimetype= 'text/html')

    servers_list = InstallServer.query.get(1)
    if servers_list == None:
        # Rename at some point.
        servers_list = add_server_list_to_db()

    servers = {}
    server_name_strings = zip(servers_list.short_names.split(','), \
                                servers_list.long_names.split(','))

    for short_names, long_names in server_name_strings:
        servers[short_names] = long_names

    return render_template("install.html", user=current_user, servers=servers, \
                                        output=output, doggo_img=get_doggo())

######### Settings Page #########

@views.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    
    flash("Redirecting to controls")
    return redirect(url_for('views.controls', server="Minecraft", command="m"))
   # return render_template("settings.html", user=current_user)

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
            new_game_server = GameServer(install_name=install_name, \
                        install_path=install_path, script_name=script_name) 
            db.session.add(new_game_server)
            db.session.commit()

            flash('Game server added!')
            return redirect(url_for('views.home'))
    
    return render_template("add.html", user=current_user)

# Helper function for del route.
def del_server(server_name):
    server = GameServer.query.filter_by(install_name=server_name).first()
    install_path = server.install_path 

    GameServer.query.filter_by(install_name=server_name).delete()
    ControlSet.query.filter_by(install_name=server_name).delete()
    db.session.commit()

# Disabled auto delete rn. Will add configparse option to disable l8t3r.
    if os.path.isdir(install_path):
        shutil.rmtree(install_path)
    
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
