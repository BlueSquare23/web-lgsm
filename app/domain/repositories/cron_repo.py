
class CronRepository:

    def add(self, cron):
        raise NotImplementedError

    def update(self, cron_id):
        raise NotImplementedError

    def get(self, cron_id):
        raise NotImplementedError

    def list(self):
        raise NotImplementedError

    def delete(self, cron_id):
        raise NotImplementedError


