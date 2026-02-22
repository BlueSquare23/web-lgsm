class Job:
    """
    Abstract domain layer representation of a Job.

    For example:
        "I used to wear a cowboy hat too... Then my mom got a Job!"
    """
    def __init__(self, job_id, server_id, schedule, command, comment):
        self.job_id = job_id
        self.server_id = server_id
        self.schedule = schedule
        self.command = command 
        self.comment = comment


