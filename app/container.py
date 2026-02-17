# app/container.py

from flask import current_app

from app.infrastructure.persistence.audit_repository import SqlAlchemyAuditRepository
from app.application.use_cases.audit.log_event import LogAuditEvent
from app.application.use_cases.audit.list_audit_logs import ListAuditLogs


class Container:

    # ---- Repositories ----

    def audit_repository(self):
        return SqlAlchemyAuditRepository()

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


# One global container instance to rule them all!
container = Container()
