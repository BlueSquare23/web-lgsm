import re
from crontab import CronTab

def list_cron(server_id):
    """
    RPC procedure to list cronjobs.
    Args:
        server_id (str): Game server UUID.

    Returns:
        str: same output as `crontab -l` package for json rpc
    """
    cron = CronTab(user=True)

    # Match any job whose comment starts with "<server_id>"
    identity_re = re.compile(rf"^{re.escape(server_id)}(,|$)")

    jobs = []
    for job in cron.find_comment(identity_re):
        jobs.append(str(job))

    payload = {"success": True, "jobs": jobs}

    return payload
