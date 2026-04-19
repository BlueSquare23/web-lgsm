import os

from flask_login import login_required, current_user
from flask import request, render_template, current_app, redirect, url_for

from app.utils import log_wrap

from app.interface.forms.views import SaveForm, UploadForm, DownloadForm
from app.interface.forms.validation_errors import validation_errors

from . import main_bp

from app.interface.use_cases import read_file, write_file, get_game_server

######### File Manager Page #########

@main_bp.route("/files", methods=["GET", "POST"])
@login_required
def files():

    save_form = SaveForm()
    upload_form = UploadForm()
    download_form = DownloadForm()

    if request.method == "GET":

        server_id = request.args.get('server_id')
        path = request.args.get('path')
        show_hidden = request.args.get("show_hidden", 1, type=int)

        current_path = None
        selected_file = None
        file_contents = None
        parent_path = None

        # Try cast to bool
        try:
            show_hidden = bool(show_hidden)
        except:
            show_hidden = False

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
                server = get_game_server(server_id)
                file_contents = read_file(server, path)

#        files = [{"name": 'fart.txt', 'path': '/home/blah/fart', 'type':'file'},
#                 {"name": 'blah.txt', 'path': '/home/blah/blah', 'type':'file'},
#                 {"name": 'test', 'path': '/home/blah/test', 'type':'dir'}]
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
            files=files,  # list of dicts: {name, path, type}
            selected_file=selected_file,
            file_contents=file_contents,
            save_form=save_form,
            upload_form=upload_form,
            show_hidden=show_hidden,
            download_form=download_form,
        )

#    # Handle Invalid form submissions.
#    if not upload_form.validate_on_submit():
#        validation_errors(upload_form)
#        return redirect(url_for("main.home"))

#    return f"Server ID: {server_id}, Target Path: {path}"




#import os

def is_dir(path):
    return os.path.isdir(path)

def list_dir_contents(directory, show_hidden=True):
    files = []

    with os.scandir(directory) as entries:
        for entry in entries:
            item_type = 'dir' if entry.is_dir(follow_symlinks=False) else 'file'

            if not show_hidden and entry.name.startswith("."):
                continue
            
            files.append({
                "name": entry.name,
                "path": entry.path,
                "type": item_type
            })

    return files
