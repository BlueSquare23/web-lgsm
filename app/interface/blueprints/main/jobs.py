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
#from app.interface.forms.views import ValidateID, JobsForm
#from app.interface.forms.validation_errors import validation_errors

from app.interface.forms import ValidateID, JobsForm, validation_errors

from . import main_bp

from app.interface.use_cases import get_template_config, check_user_access, list_user_game_servers, list_cron_jobs, list_controls, update_cron_job, get_game_server, log_audit_event


######### Jobs Route #########

@main_bp.route("/jobs", methods=["GET", "POST"])
@login_required
def jobs():
    config = get_template_config()

    # Check if user has permissions to jobs route.
    if not check_user_access(current_user.id, "jobs"):
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
        game_servers = list_user_game_servers(current_user.id)

        if request.args:
            # Checking id is valid.
            id_form = ValidateID(request.args)
            if not id_form.validate():
                validation_errors(id_form)
                return redirect(url_for("main.jobs"))

            server_id = request.args.get("server_id")
            server = get_game_server(server_id)
            server_name = server.install_name

            jobs_list = list_cron_jobs(server_id)
            current_app.logger.info(log_wrap("jobs_list", jobs_list))

            server_dict = server.__dict__
            server_json = json.dumps(server_dict)
            current_app.logger.info(log_wrap("server_json", server_json))

            # Pull in controls list from controls.json file.
            controls_list = list_controls(server.script_name, current_user)

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
            'job_id': form.job_id.data,
            'schedule': form.schedule.data,
            'command': command,
            'server_id': form.server_id.data,
            'comment': form.comment.data,
        }
        current_app.logger.debug(log_wrap("job", job))

        if update_cron_job(
                job_id=form.job_id.data,
                schedule=form.schedule.data,
                command=command,
                server_id=form.server_id.data,
                comment=form.comment.data,
            ):
            flash("Cronjob updated successfully!", category="success")
            server = get_game_server(form.server_id.data)
            log_audit_event(current_user.id,  f"User '{current_user.username}', edited cronjob for '{server.install_name}'")
            current_app.logger.info(log_wrap("request.form", request.form))

            return redirect(url_for("main.jobs", server_id=form.server_id.data))

        flash("Error adding job", category="error")
        return redirect(request.referrer)

