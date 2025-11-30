import json

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
from app.models import GameServer
from app.forms.views import ValidateID, JobsForm
from app.services.cron_service import CronService
from app.services.controls_service import ControlService

from app.config.config_manager import ConfigManager
config = ConfigManager()
controls_service = ControlService()

from . import main_bp

######### Jobs Route #########

@main_bp.route("/jobs", methods=["GET", "POST"])
@login_required
def jobs():
    global config

    # Check if user has permissions to jobs route.
    if not current_user.has_access("jobs"):
        flash(f"Your user does not have access to this page", category="error")
        return redirect(url_for("main.home"))

    # Create JobsForm.
    form = JobsForm()

    if request.method == "GET":
        server = None
        server_id = None
        server_name = None
        server_json = None
        jobs_list = []
        controls_list = []
        game_servers = GameServer.query.all()

        if request.args:
            # Checking id is valid.
            id_form = ValidateID(request.args)
            if not id_form.validate():
                validation_errors(id_form)
                return redirect(url_for("main.jobs"))

            server_id = request.args.get("server_id")
            server = GameServer.query.filter_by(id=server_id).first()
            server_name = server.install_name
            cron = CronService(server_id)
            jobs_list = cron.list_jobs()

            server_dict = server.__dict__
            del(server_dict["_sa_instance_state"])
            server_json = json.dumps(server_dict)
            current_app.logger.info(log_wrap("server_json", server_json))

            # Pull in controls list from controls.json file.
            controls_list = controls_service.get_controls(server.script_name, current_user)

            # No console for automated jobs. Don't even give the user the option to be stupid.
            form.command.choices = [ctrl.long_ctrl for ctrl in controls_list]

            if 'console' in form.command.choices:
                form.command.choices.remove('console')

            if config.getboolean('settings','allow_custom_jobs'):
                form.command.choices.append('custom')

        current_app.logger.debug(log_wrap("jobs_list", jobs_list))

        return render_template(
            "jobs.html",
            user=current_user,
            game_servers=game_servers,
            server_name=server_name,
            server_json=server_json,
            server_id=server_id,
            jobs_list=jobs_list,
            form=form,
            spinner_context="Updating Crontab",
        )

    if request.method == "POST":
        if not form.validate_on_submit():
            validation_errors(form)
            # Redirect back to the previous page.
            return redirect(request.referrer)

        # Setup custom command if send and custom.
        command = form.command.data
        if form.command.data == 'send' or form.command.data == 'custom':
            if form.custom.data == None:
                flash(f"Custom cmd required for {custom_job_type}", category="error")
                return redirect(url_for("main.jobs", server_id=form.server_id.data))

            if form.command.data == 'send':
                command = f"send {form.custom.data}"

            if form.command.data == 'custom':
                command = f"custom: {form.custom.data}"

        job = {
            'expression': form.cron_expression.data,
            'command': command,
            'server_id': form.server_id.data,
            'job_id': form.job_id.data,
            'comment': form.comment.data,
        }
        current_app.logger.debug(log_wrap("job", job))

        cron = CronService(form.server_id.data)
        if cron.edit_job(job):
            flash("Cronjob updated successfully!", category="success")
            server = GameServer.query.filter_by(id=form.server_id.data).first()
            audit_log_event(current_user.id, f"User '{current_user.username}', edited cronjob for '{server.install_name}'")
            current_app.logger.info(log_wrap("request.form", request.form))

            return redirect(url_for("main.jobs", server_id=form.server_id.data))

        flash("Error adding job", category="error")
        return redirect(request.referrer)

