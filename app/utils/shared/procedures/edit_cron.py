import os
import re
from crontab import CronTab

def edit_cron(state, **job):
    """
    User module edit cron script.
    Args:
        state (bool): Representing absent or present.
        job (Job): Job entity to update.

    Returns:
        bool: True if write successful, False otherwise.
    """
    # Identity of the job: only server_id + job_id
    identity = f"{job['server_id']}, {job['job_id']}"

    # Full comment written to the crontab (identity + optional user comment)
    comment = f"{identity},"
    if job['comment']:
        comment += f" {job['comment']}"

    script_path = os.path.join(job['install_path'], job['script_name'])
    job_cmd = f"{script_path} {job['command']}"

    custom_job_prefix = 'custom: '
    if job["command"].startswith(custom_job_prefix):
        job_cmd = job['command'].replace(custom_job_prefix, '')

    cron = CronTab(user=True)  # User rpc service user

    # Remove existing job with same identity (idempotent behavior)
    # Match any job whose comment starts with "<server_id>, <job_id>"
    # followed by a comma or end of string, regardless of the trailing comment.
    identity_re = re.compile(rf"^{re.escape(identity)}(,|$)")
    cron.remove_all(comment=identity_re)

    # Do job edit
    if state:
        cronjob = cron.new(command=job_cmd, comment=comment)
        cronjob.setall(job['schedule'])

    try:
        cron.write()
        return True
    except:
        return False
