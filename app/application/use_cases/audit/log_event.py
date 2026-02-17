import shortuuid
from datetime import datetime

from app.domain.entities.audit import Audit

class LogAuditEvent:

    def __init__(self, audit_repository, logger):
        self.audit_repository = audit_repository
        self.logger = logger

    def execute(self, user_id, message):
        audit = Audit(
            id=str(shortuuid.uuid()),
            user_id=user_id,
            username=None,
            message=message,
            date_created=datetime.utcnow(),
        )

        self.audit_repository.add(audit)

        # enforce 1000 limit
        count = self.audit_repository.count()
        if count > 1000:
            self.audit_repository.delete_oldest(count - 1000)

        self.logger.info(message)

