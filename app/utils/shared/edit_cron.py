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

    comment = f"{job['server_id']}, {job['job_id']},".strip()
    if job['comment']:
        comment = comment + f" {job['comment']}"
    job_cmd = f"{job['install_path']}/{job['script_name']} {job['command']}"

    print("comment " + comment)

    custom_job_prefix = 'custom: '
    if job["command"].startswith(custom_job_prefix):
        job_cmd = job['command'].replace(custom_job_prefix, '')

    cron = CronTab(user=True)  # User module script user

    # Remove existing job with same comment (idempotent behavior)
    cron.remove_all(comment=comment)

    # Do job edit
    if state:
        cronjob = cron.new(command=job_cmd, comment=comment)
        cronjob.setall(job['schedule'])

    try:
        cron.write()
        return True
    except:
        return False
