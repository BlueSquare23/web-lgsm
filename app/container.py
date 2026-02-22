# app/container.py

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

class Container:

    # ---- Repositories ----

    def audit_repository(self):
        return SqlAlchemyAuditRepository()

    def cron_repository(self):
        return SqlAlchemyCronRepository()


    # ---- System Interfaces ----

    def cron_scheduler(self):
        return CronScheduler()


    # ---- Use Cases ----

    def log_audit_event(self):
        return LogAuditEvent(
            audit_repository=self.audit_repository(),
            logger=current_app.audit_logger,
        )

    def list_audit_logs(self):
        return ListAuditLogs(
            audit_repository=self.audit_repository(),
        )

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

# One global container instance to rule them all!
container = Container()
