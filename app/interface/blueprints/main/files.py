import os
import io
import json

from flask_login import login_required, current_user
from flask import request, render_template, current_app, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename

from app.utils import log_wrap

from app.interface.forms import SaveForm, UploadForm, DownloadForm, validation_errors

from . import main_bp

from app.interface.use_cases import read_file, write_file, list_dir, get_game_server, list_user_game_servers, log_audit_event, getboolean_config, check_user_access


######### File Manager Page #########

@main_bp.route("/files", methods=["GET", "POST"])
@login_required
def files():

    if not getboolean_config('settings','file_manager'):
        flash("File manager disabled", category="error")
        return redirect(url_for("main.home"))

    if not check_user_access(current_user.id, "files"):
        flash("Your user does not have access to this page", category="error")
        return redirect(url_for("main.home"))

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

        if "download_submit" in request.args.keys():
            download_form = DownloadForm(request.args)
            if not download_form.validate():
                validation_errors(download_form)
                return redirect(url_for("main.home"))

            server_id = download_form.server_id.data
            path = download_form.path.data
            server = get_game_server(server_id)

            log_audit_event(current_user.id,  f"User '{current_user.username}', downloaded config '{path}'")

            file_contents = read_file(server, path)

            if file_contents is None:
                flash("Problem retrieving file contents", category="error")
                return redirect(url_for("main.home"))

            filename = os.path.basename(path)

            return send_file(
                io.BytesIO(file_contents.encode("utf-8")),
                as_attachment=True,
                download_name=filename,
                mimetype="text/plain",
            )

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

            if os.path.isdir(path):
                current_path = path
                files = list_dir(server, path, show_hidden)

            # strip file name and get listing of basedir
            else:
                selected_file = os.path.basename(path)
                base_dir = os.path.dirname(path)
                current_path = base_dir

                # handle case where file is in current directory
                if base_dir == "":
                    base_dir = "."

                files = list_dir(server, base_dir, show_hidden)

            # If file read contents
            if selected_file:
                file_contents = read_file(server, path)

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

    ## POSTs

    if request.method == "POST":

        if not check_user_access(current_user.id, "files_edit"):
            flash("Your user does not have access to write or upload files", category="error")
            return redirect(url_for("main.files"))

        # Save file
        if "save_submit" in request.form:
            if not save_form.validate_on_submit():
                validation_errors(save_form)
                return redirect(url_for("main.files"))

            server_id = save_form.server_id.data
            path = save_form.path.data
            new_file_contents = save_form.file_contents.data
            server = get_game_server(server_id)

            if write_file(server, path, new_file_contents):
                flash("File updated!", "success")
                log_audit_event(current_user.id, f"User '{current_user.username}', edited '{path}'")
            else:
                flash("Error writing to file!", "error")

            return redirect(url_for("main.files", server_id=server_id, path=path))

        # Upload file
        elif "upload_submit" in request.form:
            if not upload_form.validate_on_submit():
                validation_errors(upload_form)
                return redirect(url_for("main.files"))

            server_id = upload_form.server_id.data
            path = upload_form.path.data
            file = upload_form.file.data
            server = get_game_server(server_id)

            # Sanitize filename
            filename = secure_filename(file.filename)

            save_path = os.path.join(path, filename)

            # Security check
            if not is_safe_path(save_path, server.username):
                flash("Invalid upload path!", "error")
                return redirect(url_for("main.files", server_id=server_id))

            # Read upload bytes.
            file_contents = file.read()
            write_file(server, save_path, file_contents)

            log_audit_event(current_user.id, f"Uploaded file '{save_path}'")
            flash("File uploaded!", "success")

            return redirect(url_for("main.files", server_id=server_id, path=path))


from pathlib import Path

# TODO: I think this is basically going to be replaced by the other use cases I'm creating.
def is_safe_path(path, username):
    base_dir = Path(f"/home/{username}").resolve()
    target_path = Path(path).resolve()

    try:
        target_path.relative_to(base_dir)
        return True
    except ValueError:
        return False

