from flask_login import login_required, current_user
from flask import (
    render_template,
    request,
    flash,
    url_for,
    redirect,
    current_app,
)

from app.utils import *
#from app.models import GameServer
from app.interface.forms.views import UploadTextForm, DownloadCfgForm, SelectCfgForm
from app.managers import FileManager
from app.services import UserModuleService

from app.config.config_manager import ConfigManager
from app.container import container

config = ConfigManager()

from . import main_bp

######### Edit Route #########

@main_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    global config
    # NOTE: The abbreviation cfg will be used to refer to any lgsm game server
    # specific config files. Whereas, the word config will be used to refer to
    # any web-lgsm config info.

    if not container.check_user_access().execute(current_user.id, "edit"):
        flash("Your user does not have access to this page!", category="error")
        return redirect(url_for("main.home"))

    if not config.getboolean('settings','cfg_editor'):
        flash("Config Editor Disabled", category="error")
        return redirect(url_for("main.home"))

    upload_form = UploadTextForm()
    download_form = DownloadCfgForm()

    if request.method == "GET":
        current_app.logger.debug(request.args.keys())
        if "download_submit" in request.args.keys():
            download_form = DownloadCfgForm(request.args)
            if not download_form.validate():
                validation_errors(download_form)
                return redirect(url_for("main.home"))

            server_id = download_form.server_id.data
            cfg_path = download_form.cfg_path.data
#            server = GameServer.query.filter_by(id=server_id).first()
            server = container.get_game_server().execute(server_id)
            file_manager = FileManager(server, UserModuleService())

            container.log_audit_event().execute(current_user.id,  f"User '{current_user.username}', downloaded config '{cfg_path}'")
            return file_manager.download_file(cfg_path)

        # Convert raw get args into select_form args.
        select_form = SelectCfgForm(request.args)
        if not select_form.validate():
            validation_errors(select_form)
            return redirect(url_for("main.home"))

        server_id = select_form.server_id.data
        cfg_path = select_form.cfg_path.data
#        server = GameServer.query.filter_by(id=server_id).first()
        server = container.get_game_server().execute(server_id)

        current_app.logger.info(log_wrap("server_id", server_id))
        current_app.logger.info(log_wrap("cfg_path", cfg_path))
        current_app.logger.info(log_wrap("server", server))

        file_manager = FileManager(server, UserModuleService())
        file_contents = file_manager.read_file(cfg_path)

        if file_contents == None:
            flash("Error reading file!", category="error")
            return redirect(url_for("main.home"))

        return render_template(
            "edit.html",
            user=current_user,
            server_id=server.id,
            cfg_file=cfg_path,
            file_contents=file_contents,
            download_form=download_form,
            upload_form=upload_form,
        )

    # Handle POSTs.

    # Handle Invalid form submissions.
    if not upload_form.validate_on_submit():
        validation_errors(upload_form)
        return redirect(url_for("main.home"))

    # Process form submissions.
    server_id = upload_form.server_id.data
    cfg_path = upload_form.cfg_path.data
    new_file_contents = upload_form.file_contents.data
#    server = GameServer.query.filter_by(id=server_id).first()
    server = container.get_game_server().execute(server_id)
    file_manager = FileManager(server, UserModuleService())

    if file_manager.write_file(cfg_path, new_file_contents):
        flash("Cfg file updated!", category="success")
        container.log_audit_event().execute(current_user.id, f"User '{current_user.username}', edited '{cfg_path}'")
    else:
        flash("Error writing to cfg file!", category="error")

    return redirect(url_for("main.edit", server_id=server_id, cfg_path=cfg_path))


