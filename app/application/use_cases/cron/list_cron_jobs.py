# TODO: We need to make this use the repository and scheduler to list jobs
# eventually. Right now we're just listing the real OS crontab jobs via the
# scheduler. Eventually, we want to get existing saved jobs from the DB (aka
# repository) and get any other non-db-tracked system jobs via the scheduler.

class ListCronJobs:

    def __init__(self, cron_scheduler):
#        self.cron_repository = cron_repository
        self.cron_scheduler = cron_scheduler

    def execute(self, server_id):
        return self.cron_scheduler.list(server_id)

