# Wiring code, pull in layers for main app.

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


class Container:

    # ---- Repositories ----

    def audit_repository(self):
        return SqlAlchemyAuditRepository()

    def cron_repository(self):
        return SqlAlchemyCronRepository()

    def user_repository(self):
        return SqlAlchemyUserRepository()


    # ---- System Interfaces ----

    def cron_scheduler(self):
        return CronScheduler()


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


# One global container instance to rule them all!
container = Container()
