""" 
Wiring code, pull in layers for use in interface code via dep inversion.

This is the composition root. Its the one place in the entire application
that's allowed to know about everything. All the concrete implementations, all
the repositories, all the wiring. It's "dirty" by design so everything else can
stay clean. Think of it as the place where all the abstraction debt gets paid.
"""

from flask import current_app

# NOTE: Dirs have full names, files have abbreviations.

# Audit
from app.infrastructure.persistence.repositories.audit_repo import SqlAlchemyAuditRepository
from app.application.use_cases.audit.log_event import LogAuditEvent
from app.application.use_cases.audit.list_audit_logs import ListAuditLogs

# Cron
from app.infrastructure.persistence.repositories.cron_repo import SqlAlchemyCronRepository
from app.infrastructure.system.cron.cron_scheduler import CronScheduler
from app.application.use_cases.cron.update_cron_job import UpdateCronJob
from app.application.use_cases.cron.delete_cron_job import DeleteCronJob
from app.application.use_cases.cron.list_cron_jobs import ListCronJobs

# User
from app.infrastructure.persistence.repositories.user_repo import SqlAlchemyUserRepository
from app.application.use_cases.user.to_user import ToUser
from app.application.use_cases.user.list_users import ListUsers
from app.application.use_cases.user.get_user import GetUser
from app.application.use_cases.user.query_user import QueryUser
from app.application.use_cases.user.edit_user import EditUser 
from app.application.use_cases.user.check_user_access import CheckUserAccess
from app.application.use_cases.user.delete_user import DeleteUser
from app.application.use_cases.user.get_user_totp_uri import GetUserTotpUri
from app.application.use_cases.user.verify_user_totp import VerifyUserTotp

# GameServer
from app.infrastructure.persistence.repositories.game_server_repo import SqlAlchemyGameServerRepository
from app.infrastructure.system.game_server.game_server_manager import GameServerManager
from app.infrastructure.system.game_server.install_manager import GameServerInstallManager
from app.infrastructure.system.game_server.cfg_manager import CfgManager
from app.application.use_cases.game_server.list_game_servers import ListGameServers
from app.application.use_cases.game_server.get_game_server import GetGameServer
from app.application.use_cases.game_server.get_game_server_power_state import GetGameServerPowerState
from app.application.use_cases.game_server.query_game_server import QueryGameServer
from app.application.use_cases.game_server.edit_game_server import EditGameServer
from app.application.use_cases.game_server.delete_game_server import DeleteGameServer
from app.application.use_cases.game_server.find_cfg_paths import FindGameServerCfgPaths
from app.application.use_cases.game_server.cancel_game_server_install import CancelGameServerInstall
from app.application.use_cases.game_server.list_running_installs import ListRunningGameServerInstalls
from app.application.use_cases.game_server.list_installable import ListInstallableGameServers
from app.application.use_cases.game_server.clean_install_buffer_output import ClearInstallBufferOutput

# Blocklist
from app.infrastructure.security.blocklist_repo import InMemBlocklistRepository
from app.application.use_cases.blocklist.check_blocked import IsBlockedBlocklist
from app.application.use_cases.blocklist.add_failed import AddFailedBlocklist

# SystemMetrics
from app.infrastructure.system.metrics.system_metrics import SystemMetrics
from app.application.use_cases.metrics.get_host_stats import GetHostStats

# Processes
from app.infrastructure.system.repositories.proc_info_repo import InMemProcInfoRepository
from app.application.use_cases.processes.get_process import GetProcess
from app.application.use_cases.processes.list_processes import ListProcesses
from app.application.use_cases.processes.add_process import AddProcess
from app.application.use_cases.processes.remove_process import RemoveProcess

# Command
from app.infrastructure.system.command_executor.command_executor import CommandExecutor
from app.application.use_cases.command.run_cmd import RunCommand

# Config
from app.infrastructure.system.config.config_manager import ConfigManager
from app.application.use_cases.config.get_config import GetConfig
from app.application.use_cases.config.get_template_config import GetTemplateConfig
from app.application.use_cases.config.getboolean_config import GetBoolConfig
from app.application.use_cases.config.getint_config import GetIntConfig
from app.application.use_cases.config.set_config import SetConfig

# Files
from app.infrastructure.system.file_system.file_manager import FileManager
from app.application.use_cases.file_system.read_file import ReadFile
from app.application.use_cases.file_system.write_file import WriteFile 

# Controls
from app.infrastructure.system.repositories.controls_repo import ControlsRepository
from app.application.use_cases.controls.list_controls import ListControls

# Sudoers
from app.infrastructure.system.user.sudoers_service import SudoersService
from app.application.use_cases.sudoers.check_sudoers_access import CheckSudoersAccess
from app.application.use_cases.sudoers.add_sudoers_rule import AddSudoersRule

# Tmux
from app.infrastructure.system.game_server.tmux_socket_name_cache import TmuxSocketNameCache
from app.application.use_cases.tmux.get_tmux_socket_name import GetTmuxSocketName

# LGSM
from app.infrastructure.system.lgsm.lgsm_manager import LgsmManager
from app.application.use_cases.lgsm.check_and_get_lgsmsh import CheckAndGetLgsmsh

class Container:

    # ---- Repositories ----

    def audit_repository(self):
        return SqlAlchemyAuditRepository()

    def cron_repository(self):
        return SqlAlchemyCronRepository()

    def user_repository(self):
        return SqlAlchemyUserRepository()

    def game_server_repository(self):
        return SqlAlchemyGameServerRepository()

    def in_mem_blocklist_repository(self):
        return InMemBlocklistRepository()

    def in_mem_process_repository(self):
        return InMemProcInfoRepository()

    def controls_repository(self):
        return ControlsRepository()

    # ---- System Interfaces ----

    def cron_scheduler(self):
        return CronScheduler()

    def game_server_manager(self):
        return GameServerManager()

    def game_server_install_manager(self):
        return GameServerInstallManager()

    def system_metrics(self):
        return SystemMetrics()

    def command_executor(self):
        return CommandExecutor()

    def config_manager(self):
        return ConfigManager()

    def cfg_manager(self):
        return CfgManager()

    def file_manager(self):
        return FileManager()

    def sudoers_service(self):
        return SudoersService()

    def tmux_socket_cache_handler(self):
        return TmuxSocketNameCache()

    def lgsm_manager(self):
        return LgsmManager(
            logger=current_app.logger,  # I don't love this dep inversion but its fine for now
        )

    # ---- Use Cases ----

    ## Audit

    def log_audit_event(self):
        return LogAuditEvent(
            audit_repository=self.audit_repository(),
            logger=current_app.audit_logger,
        )

    def list_audit_logs(self):
        return ListAuditLogs(
            audit_repository=self.audit_repository(),
        )

    ## Cron

    def update_cron_job(self):
        return UpdateCronJob(
            cron_repository=self.cron_repository(),
            cron_scheduler=self.cron_scheduler(),
        )

    def delete_cron_job(self):
        return DeleteCronJob(
            cron_repository=self.cron_repository(),
            cron_scheduler=self.cron_scheduler(),
        )

    def list_cron_jobs(self):
        return ListCronJobs(
            cron_scheduler=self.cron_scheduler(),
        )

    ## User

    def to_user(self):
        return ToUser(
            user_repository=self.user_repository(),
        )

    def list_users(self):
        return ListUsers(
            user_repository=self.user_repository(),
        )

    def get_user(self):
        return GetUser(
            user_repository=self.user_repository(),
        )

    def query_user(self):
        return QueryUser(
            user_repository=self.user_repository(),
        )

    def edit_user(self):
        return EditUser(
            user_repository=self.user_repository(),
        )

    def check_user_access(self):
        return CheckUserAccess(
            user_repository=self.user_repository(),
        )

    def delete_user(self):
        return DeleteUser(
            user_repository=self.user_repository(),
        )

    def get_user_totp_uri(self):
        return GetUserTotpUri(
            user_repository=self.user_repository(),
        )

    def verify_user_totp(self):
        return VerifyUserTotp(
            user_repository=self.user_repository(),
        )

    ## GameServer

    def list_game_servers(self):
        return ListGameServers(
            game_server_repository=self.game_server_repository(),
        )

    def get_game_server(self):
        return GetGameServer(
            game_server_repository=self.game_server_repository(),
        )

    def get_game_server_power_state(self):
        return GetGameServerPowerState(
            game_server_manager=self.game_server_manager(),
        )

    def query_game_server(self):
        return QueryGameServer(
            game_server_repository=self.game_server_repository(),
        )

    def edit_game_server(self):
        return EditGameServer(
            game_server_repository=self.game_server_repository(),
        )

    def delete_game_server(self):
        return DeleteGameServer(
            game_server_repository=self.game_server_repository(),
            game_server_manager=self.game_server_manager(),
        )

    def find_cfg_paths(self):
        return FindGameServerCfgPaths(
            cfg_manager=self.cfg_manager(),
        )

    ## GameServer Installs

    def cancel_game_server_install(self):
        return CancelGameServerInstall(
            install_manager=self.game_server_install_manager(),
        )

    def list_installable_game_servers(self):
        return ListInstallableGameServers(
            install_manager=self.game_server_install_manager(),
        )

    def list_running_game_server_installs(self):
        return ListRunningGameServerInstalls(
            install_manager=self.game_server_install_manager(),
        )

    def clear_install_buffer_output(self):
        return ClearInstallBufferOutput(
            install_manager=self.game_server_install_manager(),
        )

    ## Blocklist

    def add_failed_blocklist(self):
        return AddFailedBlocklist(
            blocklist_repository=self.in_mem_blocklist_repository(),
        )

    def is_blocked_blocklist(self):
        return IsBlockedBlocklist(
            blocklist_repository=self.in_mem_blocklist_repository(),
        )

    ## SystemMetrics

    def get_host_stats(self):
        return GetHostStats(
            system_metrics=self.system_metrics(),
        )

    ## Processes

    def get_process(self):
        return GetProcess(
            process_repository=self.in_mem_process_repository()
        )

    def list_processes(self):
        return ListProcesses(
            process_repository=self.in_mem_process_repository()
        )

    def add_process(self):
        return AddProcess(
            process_repository=self.in_mem_process_repository()
        )

    def remove_process(self):
        return RemoveProcess(
            process_repository=self.in_mem_process_repository()
        )

    ## Command
    def run_command(self):
        return RunCommand(
            command_executor=self.command_executor()
        )

    ## Config

    def get_template_config(self):
        return GetTemplateConfig(
            config_manager=self.config_manager()
        )

    def get_config(self):
        return GetConfig(
            config_manager=self.config_manager()
        )

    def getboolean_config(self):
        return GetBoolConfig(
            config_manager=self.config_manager()
        )

    def getint_config(self):
        return GetIntConfig(
            config_manager=self.config_manager()
        )

    def set_config(self):
        return SetConfig(
            config_manager=self.config_manager()
        )

    ## File System

    def read_file(self):
        return ReadFile(
            file_manager=self.file_manager()
        )

    def write_file(self):
        return WriteFile(
            file_manager=self.file_manager()
        )

    ## Controls

    def list_controls(self):
        return ListControls(
            controls_repository=self.controls_repository()
        )

    ## Sudoers

    def check_sudoers_access(self):
        return CheckSudoersAccess(
            sudoers_service=self.sudoers_service()
        )

    def add_sudoers_rule(self):
        return AddSudoersRule(
            sudoers_service=self.sudoers_service()
        )

    ## Tmux

    def get_tmux_socket_name(self):
        return GetTmuxSocketName(
            tmux_socket_cache_handler=self.tmux_socket_cache_handler()
        )

    ## LGSM

    def check_and_get_lgsmsh(self):
        return CheckAndGetLgsmsh(
            lgsm_manager=self.lgsm_manager(),
        )


# One global container instance to rule them all!
container = Container()

