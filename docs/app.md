```mermaid
---
title: web-lgsm
---
classDiagram
    class AddFailedBlocklist {
        - \_\_init__(self, blocklist_repository) None
        + execute(self, ip)
    }

    class AddForm {
        + Any server_id
        + Any install_type
        + Any install_name
        + Any install_path
        + Any installable
        + dict servers
        + Any script_name
        + Any username
        + Any install_host
    }

    class AddProcess {
        - \_\_init__(self, process_repository) None
        + execute(self, server_id, proc_info)
    }

    class AddSudoersRule {
        - \_\_init__(self, sudoers_service) None
        + execute(self, username)
    }

    class Audit {
        - \_\_init__(self, id, user_id, username, message, date_created) None
    }

    class AuditModel {
        + Any id
        + Any user_id
        + Any message
        + Any date_created
        + Any user
        - \_\_repr__(self) str
        - \_\_str__(self) str
    }

    class AuditRepository {
        + add(self, audit)
        + list(self, page, per_page, user_id, search)
        + count(self)
        + delete_oldest(self, number_to_delete)
    }

    class AuthUser {
        - \_\_init__(self, user_id) None
        + get_id(self)
    }

    class CommandExecutor {
        + Any USER
        - \_\_init__(self, config) None
        - \_get_local_executor(self)
        - \_get_ssh_executor(self)
        - \_get_executor(self, server_type, **kwargs)
        + run(self, cmd, server, cmd_id, app_context, timeout, **kwargs)
    }

    class BaseCommandExecutor {
        - \_\_init__(self, logger) None
        - \_setup_proc_info(self, cmd_id, create)
        - \_process_output_line(self, line, output_type, proc_info)
        - \_log_wrap(self, stream_type, message)
        - \_process_raw_output(self, raw_line, proc_info, output_type)
    }

    class BatchUpdateConfig {
        - \_\_init__(self, config_manager) None
        + execute(self)
    }

    class BlocklistRepository {
        + add(self, ip)
        + check(self, ip)
    }

    class CancelGameServerInstall {
        - \_\_init__(self, install_manager) None
        + execute(self, pid)
    }

    class CfgManager {
        + Any USER
        - \_\_init__(self, executor, proc_info_repo, command_executor, logger) None
        + find_cfg_paths(self, server)
        + find_cfg_paths_ssh(self, server, valid_gs_cfgs)
    }

    class CheckAndGetLgsmsh {
        - \_\_init__(self, lgsm_manager) None
        + execute(self, lgsmsh_path)
    }

    class CheckSudoersAccess {
        - \_\_init__(self, sudoers_service) None
        + execute(self, username)
    }

    class CheckUserAccess {
        - \_\_init__(self, user_repository) None
        + execute(self, user_id, route, server_id)
    }

    class ClearInstallBufferOutput {
        - \_\_init__(self, install_manager) None
        + execute(self, server_id, app_context)
    }

    class CmdOutput {
        + get(self, server_id)
    }

    class ColorField {
        + Any widget
    }

    class ConditionalPasswordRequired {
        - \_\_init__(self, message) None
        - \_\_call__(self, form, field)
    }

    class ConfigManager {
        + Any \_DEFAULTS
        - \_\_init__(self) None
        + reload(self)
        + get(self, section, option, fallback)
        - \_get_default(self, section, option)
        + getboolean(self, section, option, fallback)
        + getint(self, section, option, fallback)
        - \_\_getitem__(self, section)
        + set(self, section, option, value, immediate)
        + batch_update(self)
        - \_write_config(self)
    }

    class Container {
        + audit_repository(self)
        + cron_repository(self)
        + user_repository(self)
        + game_server_repository(self)
        + in_mem_blocklist_repository(self)
        + in_mem_process_repository(self)
        + controls_repository(self)
        + cron_scheduler(self)
        + game_server_manager(self)
        + game_server_install_manager(self)
        + system_metrics(self)
        + command_executor(self)
        + config_manager(self)
        + cfg_manager(self)
        + file_manager(self)
        + sudoers_service(self)
        + tmux_socket_cache_handler(self)
        + lgsm_manager(self)
        + log_audit_event(self)
        + list_audit_logs(self)
        + update_cron_job(self)
        + delete_cron_job(self)
        + list_cron_jobs(self)
        + to_user(self)
        + list_users(self)
        + get_user(self)
        + query_user(self)
        + edit_user(self)
        + check_user_access(self)
        + delete_user(self)
        + get_user_totp_uri(self)
        + verify_user_totp(self)
        + list_user_game_servers(self)
        + list_game_servers(self)
        + get_game_server(self)
        + get_game_server_power_state(self)
        + query_game_server(self)
        + edit_game_server(self)
        + delete_game_server(self)
        + find_cfg_paths(self)
        + cancel_game_server_install(self)
        + list_installable_game_servers(self)
        + list_running_game_server_installs(self)
        + clear_install_buffer_output(self)
        + add_failed_blocklist(self)
        + is_blocked_blocklist(self)
        + get_host_stats(self)
        + get_process(self)
        + list_processes(self)
        + add_process(self)
        + remove_process(self)
        + run_command(self)
        + get_template_config(self)
        + get_config(self)
        + getboolean_config(self)
        + getint_config(self)
        + set_config(self)
        + batch_update_config(self)
        + read_file(self)
        + write_file(self)
        + list_controls(self)
        + check_sudoers_access(self)
        + add_sudoers_rule(self)
        + get_tmux_socket_name(self)
        + check_and_get_lgsmsh(self)
    }

    class Control {
        - \_\_init__(self) None
        - \_\_str__(self) str
        - \_\_repr__(self) str
    }

    class ControlsRepository {
        - \_\_init__(self, controls_file, exemptions_file) None
        + load_data(self)
        + list(self, server, user)
        - \_filter_controls_by_permissions(self, controls_dict, user)
    }

    class CronModel {
        + Any id
        + Any server_id
        + Any command
        + Any comment
        + Any schedule
        + Any date_created
        + Any game_server
        - \_\_repr__(self) str
        - \_\_str__(self) str
    }

    class CronRepository {
        + add(self, cron)
        + update(self, cron_id)
        + get(self, cron_id)
        + list(self)
        + delete(self, cron_id)
    }

    class CronScheduler {
        + list CONNECTOR_CMD
        - \_\_init__(self, command_service, module_service, game_server_repo, cron_repo) None
        + update(self, job, state)
        + delete(self, job_id)
        + list(self, server_id)
        + parse_cron_jobs(self, cron_text, target_uuid)
    }

    class DeleteCronJob {
        - \_\_init__(self, cron_repository, cron_scheduler) None
        + execute(self, job_id)
    }

    class DeleteGameServer {
        - \_\_init__(self, game_server_repository, game_server_manager) None
        + execute(self, id, remove_files, delete_user, errors)
    }

    class DeleteUser {
        - \_\_init__(self, user_repository) None
        + execute(self, id)
    }

    class DownloadCfgForm {
        + Any server_id
        + Any cfg_path
        + Any download_submit
    }

    class DummyConfig {
        + getboolean(self, *_)
    }

    class EditGameServer {
        - \_\_init__(self, game_server_repository) None
        + execute(self, id, install_name, install_path, script_name, username, install_type, is_container, install_host, install_finished, install_failed, keyfile_path, sort_order)
    }

    class EditUser {
        - \_\_init__(self, user_repository) None
        + execute(self, id, username, password, role, permissions, otp_secret, otp_enabled, otp_setup)
    }

    class EditUsersForm {
        + Any selected_user
        + Any change_username_password
        + Any username
        + Any password1
        + Any password2
        + Any is_admin
        + Any enable_otp
        + list route_choices
        + Any routes
        + Any controls
        + Any server_ids
    }

    class FailingClientInterface {
        + get_client(self, username, hostname)
    }

    class FakeChannel {
        - \_\_init__(self, stdout, stderr, exit_status) None
        + set_combine_stderr(self, val)
        + exec_command(self, cmd)
        + settimeout(self, timeout)
        + recv_ready(self)
        + recv(self, n)
        + recv_stderr_ready(self)
        + recv_stderr(self, n)
        + exit_status_ready(self)
        + recv_exit_status(self)
    }

    class FakeFile {
        - \_\_init__(self, content, should_fail) None
        + read(self)
        + write(self, data)
        - \_\_enter__(self)
        - \_\_exit__(self, exc_type, exc, tb)
    }

    class FakeParamikoClient {
        - \_\_init__(self) None
        + set_missing_host_key_policy(self, policy)
        + connect(self, hostname, username, key_filename, timeout, look_for_keys, allow_agent)
        + exec_command(self, cmd, timeout)
        + close(self)
    }

    class FakeSFTP {
        - \_\_init__(self, file_obj) None
        + open(self, path, mode)
        - \_\_enter__(self)
        - \_\_exit__(self, exc_type, exc, tb)
    }

    class FakeSSHClient {
        - \_\_init__(self, file_obj) None
        + open_sftp(self)
    }

    class FakeSSHClientInterface {
        - \_\_init__(self, file_obj) None
        + get_client(self, username, hostname)
    }

    class FakeTransport {
        - \_\_init__(self, channel) None
        + open_session(self)
    }

    class FileInterface {
        - \_\_init__(self, server, logger) None
        + read_file(self, file_path)
        + write_file(self, file_path, content)
    }

    class FileManager {
        - \_\_init__(self, executor) None
        + interface(self)
        + read(self, server, file_path)
        + write(self, server, file_path, content)
    }

    class FindGameServerCfgPaths {
        - \_\_init__(self, cfg_manager) None
        + execute(self, server)
    }

    class GameServer {
        - \_\_init__(self, id, install_name, install_path, script_name, username, install_type, is_container, install_host, install_finished, install_failed, keyfile_path, sort_order) None
    }

    class GameServerDelete {
        + delete(self, server_id)
    }

    class GameServerInstallManager {
        + list CONNECTOR_CMD
        - \_\_init__(self, game_server_repository, logger) None
        + list(self)
        + cancel(self, pid)
        + list_running(self)
        + clear_proc_info_post_install(self, server_id, app_context)
    }

    class GameServerManager {
        + Any CWD
        + list CONNECTOR_CMD
        + Any USER
        - \_\_init__(self, logger) None
        - \_normalize_path(self, path)
        + delete(self, server, delete_user, errors)
        + get_power_state(self, server)
    }

    class GameServerModel {
        + Any id
        + Any install_name
        + Any install_path
        + Any script_name
        + Any username
        + Any is_container
        + Any install_type
        + Any install_host
        + Any install_finished
        + Any install_failed
        + Any keyfile_path
        + Any sort_order
        - \_\_repr__(self) str
        - \_\_str__(self) str
    }

    class GameServerRepository {
        + add(self, game_server)
        + update(self, game_server)
        + get(self, id)
        + list(self)
        + delete(self, id)
    }

    class GetBoolConfig {
        - \_\_init__(self, config_manager) None
        + execute(self, section, option, fallback)
    }

    class GetConfig {
        - \_\_init__(self, config_manager) None
        + execute(self, section, option, fallback)
    }

    class GetGameServer {
        - \_\_init__(self, game_server_repository) None
        + execute(self, game_server_id)
    }

    class GetGameServerPowerState {
        - \_\_init__(self, game_server_manager) None
        + execute(self, game_server_id)
    }

    class GetHostStats {
        - \_\_init__(self, system_metrics) None
        + execute(self)
    }

    class GetIntConfig {
        - \_\_init__(self, config_manager) None
        + execute(self, section, option, fallback)
    }

    class GetProcess {
        - \_\_init__(self, process_repository) None
        + execute(self, server_id, create)
    }

    class GetTemplateConfig {
        - \_\_init__(self, config_manager) None
        + execute(self)
    }

    class GetTmuxSocketName {
        - \_\_init__(self, tmux_socket_cache_handler) None
        + execute(self, server)
    }

    class GetUser {
        - \_\_init__(self, user_repository) None
        + execute(self, user_id)
    }

    class GetUserTotpUri {
        - \_\_init__(self, user_repository) None
        + execute(self, user_id)
    }

    class InMemBlocklistRepository {
        + int max_fail
        + list allowlist
        + Any blocklist
        + Any failed
        - \_\_new__(cls)
        + add(self, ip)
        + check(self, ip)
    }

    class InMemProcInfoRepository {
        + Any processes
        - \_\_new__(cls)
        + list(self)
        + add(self, server_id, proc_info)
        + get(self, server_id, create)
        + remove(self, server_id)
    }

    class IsBlockedBlocklist {
        - \_\_init__(self, blocklist_repository) None
        + execute(self, ip)
    }

    class Job {
        - \_\_init__(self, job_id, server_id, schedule, command, comment) None
    }

    class JobsForm {
        + Any command
        + Any custom
        + Any comment
        + Any schedule
        + Any server_id
        + Any job_id
    }

    class LgsmManager {
        + str LINUXGSM_URL
        + int THREE_WEEKS_SECONDS
        - \_\_init__(self, logger) None
        + get_lgsmsh(self, lgsmsh_path)
        + check_and_get_lgsmsh(self, lgsmsh_path)
    }

    class ListAuditLogs {
        - \_\_init__(self, audit_repository) None
        + execute(self, page, per_page, user_id, search)
    }

    class ListControls {
        - \_\_init__(self, controls_repository) None
        + execute(self, server, user)
    }

    class ListCronJobs {
        - \_\_init__(self, cron_scheduler) None
        + execute(self, server_id)
    }

    class ListGameServers {
        - \_\_init__(self, game_server_repository) None
        + execute(self)
    }

    class ListInstallableGameServers {
        - \_\_init__(self, install_manager) None
        + execute(self)
    }

    class ListProcesses {
        - \_\_init__(self, process_repository) None
        + execute(self)
    }

    class ListRunningGameServerInstalls {
        - \_\_init__(self, install_manager) None
        + execute(self)
    }

    class ListUserGameServers {
        - \_\_init__(self, user_repository, game_server_repository) None
        + execute(self, user_id)
    }

    class ListUsers {
        - \_\_init__(self, user_repository) None
        + execute(self)
    }

    class LocalCommandExecutor {
        - \_\_init__(self, config) None
        + run(self, cmd, cmd_id, app_context, timeout)
        + get_output(self, proc, proc_info, output_type)
    }

    class LocalFileInterface {
        + Any USER
        - \_\_init__(self, server, executor) None
        + read(self, file_path)
        + write(self, file_path, content)
    }

    class LogAuditEvent {
        - \_\_init__(self, audit_repository, logger) None
        + execute(self, user_id, message)
    }

    class LoginForm {
        + Any username
        + Any password
        + Any otp_code
        + Any submit
    }

    class ManageCron {
        + check_perms(self, server_id)
        + validate_server_id(self, server_id)
        + get(self, server_id, job_id)
        + post(self, server_id, job_id)
        + delete(self, server_id, job_id)
    }

    class OTPSetupForm {
        + None user_id
        + Any otp_code
        + Any submit
    }

    class ProcInfo {
        - \_\_init__(self) None
        + toJSON(self)
        - \_\_str__(self) str
        - \_\_repr__(self) str
    }

    class ProcInfoRepository {
        + add(self, server_id, proc_info)
        + list(self)
        + get(self, server_id, create)
        + remove(self, server_id)
    }

    class QueryGameServer {
        - \_\_init__(self, game_server_repository) None
        + execute(self, **kwargs)
    }

    class QueryUser {
        - \_\_init__(self, user_repository) None
        + execute(self, key, value)
    }

    class ReadFile {
        - \_\_init__(self, file_manager) None
        + execute(self, server, file_path)
    }

    class RemoveProcess {
        - \_\_init__(self, process_repository) None
        + execute(self, server_id)
    }

    class RunCommand {
        - \_\_init__(self, command_executor) None
        + execute(self, cmd, server, cmd_id, app_context)
    }

    class SSHClientInterface {
        + get_client(self, username, hostname)
        - \_get_ssh_key_file(self, user, host)
    }

    class SSHFileInterface {
        - \_\_init__(self, server, client_interface) None
        + read(self, file_path)
        + write(self, file_path, content)
    }

    class SelectCfgForm {
        + Any server_id
        + Any cfg_path
    }

    class SendCommandForm {
        + Any send_form
        + Any server_id
        + Any control
        + Any send_cmd
        + Any submit
    }

    class ServerControlForm {
        + Any ctrl_form
        + Any server_id
        + Any control
        + Any submit
    }

    class ServerExists {
        - \_\_init__(self, message) None
        - \_\_call__(self, form, field)
    }

    class ServerListOrder {
        + post(self)
    }

    class ServerStatus {
        + get(self, server_id)
    }

    class SetConfig {
        - \_\_init__(self, config_manager) None
        + execute(self, section, option, fallback)
    }

    class SettingsForm {
        + Any text_color
        + Any graphs_primary
        + Any graphs_secondary
        + Any terminal_height
        + Any delete_user
        + Any remove_files
        + Any install_new_user
        + Any newline_ending
        + Any show_stderr
        + Any clear_output_on_reload
        + Any show_stats
        + Any purge_cache
        + Any update_weblgsm
        + Any submit
    }

    class SetupForm {
        + Any username
        + Any password1
        + Any password2
        + Any enable_otp
        + Any submit
        + validate_password1(self, field)
        + validate_password2(self, field)
    }

    class SqlAlchemyAuditRepository {
        + add(self, audit)
        + count(self)
        + delete_oldest(self, number_to_delete)
        + list(self, page, per_page, user_id, search)
    }

    class SqlAlchemyCronRepository {
        + add(self, job)
        + update(self, job)
        + get(self, job_id)
        + delete(self, job_id)
        + list(self)
    }

    class SqlAlchemyGameServerRepository {
        + add(self, game_server)
        + update(self, game_server)
        + get(self, game_server_id)
        + query(self, **kwargs)
        + delete(self, game_server_id)
        + list(self)
    }

    class SqlAlchemyUserRepository {
        + add(self, user)
        + update(self, user)
        + get(self, user_id)
        + query(self, key, value)
        + delete(self, user_id)
        + list(self)
        + to_domain(self, model)
        + get_totp_uri(self, user_id)
        + verify_totp(self, user_id, token)
        + has_access(self, user_id, route, server_id)
    }

    class SshCommandExecutor {
        - \_\_init__(self, config, client_interface) None
        + run(self, cmd, cmd_id, app_context, timeout, server)
        + get_output(self, proc, proc_info, output_type)
        - \_read_ssh_output(self, channel, proc_info)
        - \_process_ssh_chunk(self, chunk, proc_info, output_type)
    }

    class SudoersService {
        + list CONNECTOR_CMD
        - \_\_init__(self) None
        + has_access(self, username)
        + add_user(self, username)
    }

    class SystemMetrics {
        + Any prev_bytes_sent
        + Any prev_bytes_recv
        + Any prev_time
        + get_network_stats(self)
        + get_host_stats(self)
    }

    class SystemUsage {
        + get(self)
    }

    class TemplateConfig {
        - \_\_init__(self, config_manager) None
        + get(self, section, option, fallback)
        + getboolean(self, section, option, fallback)
        + getint(self, section, option, fallback)
    }

    class TestConfigManager {
        + create_test_config(self, content)
        + cleanup_test_config(self)
        + test_init_with_defaults(self)
        + test_get_with_default_fallback(self)
        + test_get_with_custom_fallback(self)
        + test_getboolean(self)
        + test_getint(self)
        + test_set_method(self)
        + test_section_access(self)
        + test_nonexistent_section(self)
        + test_batch_update_context(self)
        + test_reload_method(self)
        + teardown_method(self)
    }

    class TestSqlAlchemyCronRepoistory {
        + test_create_job(self, db_session, client, add_mock_server)
        + test_delete_job(self, db_session, client, add_mock_server)
        + test_parse_cron_jobs_empty_input(self)
        + test_parse_cron_jobs_with_valid_job(self)
        + test_edit_existing_job(self, db_session, add_mock_server)
    }

    class TestSystemMetrics {
        + test_get_network_stats(self)
        + test_get_host_stats(self)
    }

    class TmuxSocketNameCache {
        + del_socket_name_cache(self, server_id)
        + get_tmux_socket_name(self, server)
    }

    class ToUser {
        - \_\_init__(self, user_repository) None
        + execute(self, model)
    }

    class TrackingSFTP {
        - \_\_init__(self, file_obj) None
        + open(self, path, mode)
    }

    class UpdateConsole {
        + post(self, server_id)
    }

    class UpdateCronJob {
        - \_\_init__(self, cron_repository, cron_scheduler) None
        + execute(self, job_id, server_id, schedule, command, comment)
    }

    class UploadTextForm {
        + Any server_id
        + Any cfg_path
        + Any file_contents
        + Any save_submit
    }

    class User {
        - \_\_init__(self, id, username, password, role, permissions, otp_secret, otp_enabled, otp_setup) None
    }

    class UserModel {
        + Any id
        + Any username
        + Any password
        + Any role
        + Any permissions
        + Any date_created
        + Any otp_secret
        + Any otp_enabled
        + Any otp_setup
        - \_\_repr__(self) str
        - \_\_str__(self) str
        - \_\_init__(self, **kwargs) None
    }

    class UserModuleService {
        - \_\_init__(self, module_dir) None
        + call(self, func_name, *args, as_user, **kwargs)
    }

    class UserRepository {
        + add(self, user)
        + update(self, user)
        + get(self, user_id)
        + list(self)
        + delete(self, user_id)
    }

    class ValidConfigFile {
        - \_\_init__(self, message) None
        - \_\_call__(self, form, field)
    }

    class ValidCronExpr {
        - \_\_init__(self, message) None
        - \_\_call__(self, form, field)
    }

    class ValidateID {
        + Any server_id
    }

    class ValidateOTPCode {
        - \_\_init__(self, user_id, message) None
        - \_\_call__(self, form, field)
    }

    class VerifyUserTotp {
        - \_\_init__(self, user_repository) None
        + execute(self, user_id, token)
    }

    class WriteFile {
        - \_\_init__(self, file_manager) None
        + execute(self, server, file_path, content)
    }

    LoginForm --|> flask_wtf.FlaskForm

    SetupForm --|> flask_wtf.FlaskForm

    OTPSetupForm --|> flask_wtf.FlaskForm

    EditUsersForm --|> flask_wtf.FlaskForm

    AddForm --|> flask_wtf.FlaskForm

    ColorField --|> wtforms.StringField

    SettingsForm --|> flask_wtf.FlaskForm

    UploadTextForm --|> flask_wtf.FlaskForm

    DownloadCfgForm --|> flask_wtf.FlaskForm

    SelectCfgForm --|> wtforms.Form

    ValidateID --|> wtforms.Form

    SendCommandForm --|> flask_wtf.FlaskForm

    ServerControlForm --|> flask_wtf.FlaskForm

    JobsForm --|> flask_wtf.FlaskForm

    AuthUser --|> flask_login.UserMixin

    ManageCron --|> flask_restful.Resource

    UpdateConsole --|> flask_restful.Resource

    ServerStatus --|> flask_restful.Resource

    ServerListOrder --|> flask_restful.Resource

    CmdOutput --|> flask_restful.Resource

    GameServerDelete --|> flask_restful.Resource

    SystemUsage --|> flask_restful.Resource

    ControlsRepository --|> app.domain.entities.control.Control

    InMemProcInfoRepository --|> app.domain.repositories.proc_info_repo.ProcInfoRepository

    SshCommandExecutor --|> BaseCommandExecutor

    BaseCommandExecutor ..|> CommandExecutor

    LocalCommandExecutor --|> BaseCommandExecutor

    LocalFileInterface --|> FileInterface

    SSHFileInterface --|> FileInterface

    SqlAlchemyCronRepository --|> app.domain.repositories.cron_repo.CronRepository

    SqlAlchemyGameServerRepository --|> app.domain.repositories.game_server_repo.GameServerRepository

    SqlAlchemyAuditRepository --|> app.domain.repositories.audit_repo.AuditRepository

    SqlAlchemyUserRepository --|> app.domain.repositories.user_repo.UserRepository

    UserModel --|> app.db.Model

    UserModel --|> flask_login.UserMixin

    GameServerModel --|> app.db.Model

    CronModel --|> app.db.Model

    AuditModel --|> app.db.Model

    InMemBlocklistRepository --|> app.domain.repositories.blocklist_repo.BlocklistRepository

    TrackingSFTP --|> FakeSFTP
```
