from threading import Thread
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
from app.forms.views import SettingsForm

from app.config.config_manager import ConfigManager
from app.services import ControlService, CommandExecService

from . import main_bp


######### Settings Page #########

@main_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    config = ConfigManager()
    command_service = CommandExecService(config)

    # Check if user has permissions to settings route.
    if not current_user.has_access("settings"):
        flash("Your user does not have access to this page", category="error")
        return redirect(url_for("main.home"))

    # Create SettingsForm.
    form = SettingsForm()

    if request.method == "GET":
        # Set form defaults.
        form.text_color.default = config.get('aesthetic','text_color')
        form.graphs_primary.default = config.get('aesthetic','graphs_primary')
        form.graphs_secondary.default = config.get('aesthetic','graphs_secondary')
        form.terminal_height.default = config.getint('aesthetic','terminal_height')
        form.delete_user.default = str(config.getboolean('settings','delete_user')).lower()
        form.remove_files.default = str(config.getboolean('settings','remove_files')).lower()
        form.install_new_user.default = str(
            config.getboolean('settings','install_create_new_user')
        ).lower()
        form.newline_ending.default = str(config.getboolean('settings','end_in_newlines')).lower()
        form.show_stderr.default = str(config.getboolean('settings','show_stderr')).lower()
        form.clear_output_on_reload.default = str(
            config.getboolean('settings','clear_output_on_reload')
        ).lower()
        # BooleanFields handle setting default differently from RadioFields.
        if config.getboolean('aesthetic','show_stats'):
            form.show_stats.default = "true"
        form.process()  # Required to apply form changes.

        return render_template(
            "settings.html",
            user=current_user,
            system_user=USER,
            _config=config,
            form=form,
        )

    # Handle Invalid form submissions.
    if not form.validate_on_submit():
        validation_errors(form)
        return redirect(url_for("main.settings"))

    # TODO v1.9: Restructure this. These giant blocks of text aren't great, but
    # I do want to log this. Idk maybe I just log with dir or something to get
    # a deeper/dumper view of things. Wish I had perl's data dumper :(

    text_color_pref = str(form.text_color.data).lower()
    user_del_pref = str(form.delete_user.data).lower()
    file_pref = str(form.remove_files.data).lower()
    clear_output_pref = str(form.clear_output_on_reload.data).lower()
    height_pref = str(form.terminal_height.data).lower()
    update_weblgsm = str(form.update_weblgsm.data).lower()
    graphs_primary_pref = str(form.graphs_primary.data).lower()
    graphs_secondary_pref = str(form.graphs_secondary.data).lower()
    show_stats_pref = str(form.show_stats.data).lower()
    purge_cache = str(form.purge_cache.data).lower()
    install_new_user_pref = str(form.install_new_user.data).lower()
    newline_ending_pref = str(form.newline_ending.data).lower()
    show_stderr_pref = str(form.show_stderr.data).lower()

    # Debug messages.
    current_app.logger.info(log_wrap("text_color_pref", text_color_pref))
    current_app.logger.info(log_wrap("delete_user_pref", user_del_pref))
    current_app.logger.info(log_wrap("file_pref", file_pref))
    current_app.logger.info(log_wrap("clear_output_pref", clear_output_pref))
    current_app.logger.info(log_wrap("height_pref", height_pref))
    current_app.logger.info(log_wrap("update_weblgsm", update_weblgsm))
    current_app.logger.info(log_wrap("graphs_primary_pref", graphs_primary_pref))
    current_app.logger.info(log_wrap("graphs_secondary_pref", graphs_secondary_pref))
    current_app.logger.info(log_wrap("show_stats_pref", show_stats_pref))
    current_app.logger.info(log_wrap("purge_cache", purge_cache))
    current_app.logger.info(log_wrap("install_new_user_pref", install_new_user_pref))
    current_app.logger.info(log_wrap("newline_ending_pref", newline_ending_pref))
    current_app.logger.info(log_wrap("show_stderr_pref", show_stderr_pref))

    if purge_cache != None:
        cache.clear()

    # Batch update config via context handler.
    with config.batch_update() as config:
        config.set('aesthetic', 'text_color', text_color_pref)
        config.set('settings',  'delete_user', user_del_pref)
        config.set('settings',  'remove_files', file_pref)
        config.set('settings',  'clear_output_on_reload', clear_output_pref)
        config.set('aesthetic', 'terminal_height', height_pref)
        config.set('aesthetic', 'graphs_primary', graphs_primary_pref)
        config.set('aesthetic', 'graphs_secondary', graphs_secondary_pref)
        config.set('aesthetic', 'show_stats', show_stats_pref)
        config.set('settings',  'install_create_new_user', install_new_user_pref)
        config.set('settings',  'end_in_newlines', newline_ending_pref)
        config.set('settings',  'show_stderr', show_stderr_pref)

    # Update's the weblgsm.
    if update_weblgsm == "true":
        status = update_self()
        if "Error:" in status:
            flash(status, category="error")
            return redirect(url_for("main.settings"))

        flash(status)

        cmd = ["./web-lgsm.py", "--restart"]
        restart_daemon = Thread(
            target=command_service.run_command,
            args=(cmd, None, str(uuid.uuid4()), current_app.app_context()),
            daemon=True,
            name="restart",
        )
        restart_daemon.start()
        return redirect(url_for("main.settings"))

    flash("Settings Updated!")
    audit_log_event(current_user.id, f"User '{current_user.username}', changed setting(s) on settings page")
    return redirect(url_for("main.settings"))

