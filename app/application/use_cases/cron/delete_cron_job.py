class DeleteCronJob:

    def __init__(self, cron_repository, cron_scheduler):
        self.cron_repository = cron_repository
        self.cron_scheduler = cron_scheduler

    def execute(self, job_id):
        job = self.cron_repository.get(job_id)
        try:
            self.cron_scheduler.delete(job)
            self.cron_repository.delete(job_id)
        except Exception as e:
            print(e)

