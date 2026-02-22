class DeleteCronJob:

    def __init__(self, cron_repository, cron_scheduler):
        self.cron_repository = cron_repository
        self.cron_scheduler = cron_scheduler

    def execute(self, job_id):
        """
        Returns:
            Bool: True if successfully deleted, false otherwise.
        """
        job = self.cron_repository.get(job_id)

        # If we can't delete from the system, don't delete from DB.
        if self.cron_scheduler.delete(job):
            return self.cron_repository.delete(job_id)

        return False
