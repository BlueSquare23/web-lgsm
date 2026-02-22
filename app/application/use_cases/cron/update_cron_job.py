from app.domain.entities.job import Job

class UpdateCronJob:

    def __init__(self, cron_repository, cron_scheduler):
        self.cron_repository = cron_repository
        self.cron_scheduler = cron_scheduler

    def execute(self, job_id, server_id, schedule, command, comment):
        # TODO: Find a cleaner way to pack this.
        job = Job(
            job_id = job_id,
            server_id = server_id,
            schedule = schedule,
            command = command,
            comment = comment,
        )
        try:
            job.job_id = self.cron_repository.update(job)
            return self.cron_scheduler.update(job)
        except:
            return False


