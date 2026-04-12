
class AuditRepository:

    def add(self, audit):
        raise NotImplementedError

    def list(self, page, per_page, user_id=None, search=None):
        raise NotImplementedError

    def count(self):
        raise NotImplementedError

    def delete_oldest(self, number_to_delete):
        raise NotImplementedError
