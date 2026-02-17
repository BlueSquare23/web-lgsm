class ListAuditLogs:

    def __init__(self, audit_repository):
        self.audit_repository = audit_repository

    def execute(self, page, per_page, user_id=None, search=None):
        return self.audit_repository.list(
            page=page,
            per_page=per_page,
            user_id=user_id,
            search=search,
        )

