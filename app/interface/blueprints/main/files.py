import os
import json

from flask_login import login_required, current_user
from flask import request, render_template, current_app, redirect, url_for, flash

from app.utils import log_wrap

from app.interface.forms import SaveForm, UploadForm, DownloadForm, validation_errors

from . import main_bp

from app.interface.use_cases import read_file, write_file, get_game_server, list_user_game_servers

######### File Manager Page #########

@main_bp.route("/files", methods=["GET", "POST"])
@login_required
def files():

    save_form = SaveForm()
    upload_form = UploadForm()
    download_form = DownloadForm()

    game_servers = list_user_game_servers(current_user.id)

    if request.method == "GET":

        server_id = request.args.get('server_id')
        path = request.args.get('path')
        show_hidden = request.args.get("show_hidden", 1, type=int)

        current_path = None
        selected_file = None
        file_contents = None
        parent_path = None
        server_json = None

        # TODO: If server id and path are none, just plop the user down in
        # web-lgsm users home dir. Might have to think more abt how this fits
        # in with game server file system caging.

        # Try cast to bool
        try:
            show_hidden = bool(show_hidden)
        except:
            show_hidden = False

        if server_id:
            server = get_game_server(server_id)

            if server:
                server_json = json.dumps(server.__dict__)

                if path:
                    if not is_safe_path(path, server.username):
                        flash("Cannot go above game server user's home dir!", category="error")
                        return redirect(url_for("main.files", server_id=server_id, path=f"/home/{server.username}"))

                if not path:
                    path = server.install_path
        else:
            path = None

        # If target path is a dir, fetch listing of files & sub dirs.
        files = []
        if path:
            parent_path = os.path.abspath(os.path.join(path, ".."))

            if is_dir(path):
                current_path = path
                files = list_dir_contents(path, show_hidden)

            # strip file name and get listing of basedir
            else:
                selected_file = os.path.basename(path)
                base_dir = os.path.dirname(path)
                current_path = base_dir

                # handle case where file is in current directory
                if base_dir == "":
                    base_dir = "."

                files = list_dir_contents(base_dir, show_hidden)

            # If file read contents
            if selected_file:
                file_contents = read_file(server, path)

#        files = [{"name": 'fart.txt', 'path': '/home/blah/fart', 'type':'file', 'perms', '-rw-r--r--'},
#                 {"name": 'blah.txt', 'path': '/home/blah/blah', 'type':'file', 'perms', '-rw-r--r--'},
#                 {"name": 'test', 'path': '/home/blah/test', 'type':'dir', 'perms', 'drwxrwxr-x'}]
#
    
        #{
        #    "name": "server.cfg",
        #    "path": "/home/lgsm/serverfiles/server.cfg",
        #    "type": "file"  # or "dir"
        #}

#        selected_file = 'fart.txt'
#        file_contents = 'blah'

        return render_template(
            "files.html",
            user=current_user,
            server_id=server_id,
            current_path=current_path,
            parent_path=parent_path,
            files=files,
            selected_file=selected_file,
            file_contents=file_contents,
            save_form=save_form,
            upload_form=upload_form,
            show_hidden=show_hidden,
            download_form=download_form,
            game_servers=game_servers,
            server_json=server_json,
        )

#    # Handle Invalid form submissions.
#    if not upload_form.validate_on_submit():
#        validation_errors(upload_form)
#        return redirect(url_for("main.home"))

#    return f"Server ID: {server_id}, Target Path: {path}"



# TODO: Convert these into application use cases and any required infrastructure and user module service scripts.

#import os
import stat

def is_dir(path):
    return os.path.isdir(path)

def list_dir_contents(directory, show_hidden=True):
    files = []

    with os.scandir(directory) as entries:
        for entry in entries:
            item_type = 'dir' if entry.is_dir(follow_symlinks=False) else 'file'

            if not show_hidden and entry.name.startswith("."):
                continue

            info = entry.stat()

            # Get raw octal permissions (e.g., 0o644)
            perms_octal = oct(info.st_mode & 0o777)
            
            # Get readable string (e.g., '-rw-r--r--')
            perms = stat.filemode(info.st_mode)
            
            files.append({
                "name": entry.name,
                "path": entry.path,
                "type": item_type,
                "perms": perms
            })

    return files

from pathlib import Path

def is_safe_path(path, username):
    base_dir = Path(f"/home/{username}").resolve()
    target_path = Path(path).resolve()

    try:
        target_path.relative_to(base_dir)
        return True
    except ValueError:
        return False

