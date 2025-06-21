import re
import shortuuid

from cron_converter import Cron

from .models import *
from .utils import *

class Jobs:

    def __init__(self, server_id):
        self.server_id = server_id 


    def add_job(self):
        pass


    def delete_job(self):
        pass


    def list_jobs(self):
        """
        Used for getting list of jobs for associated game server.

        Returns:
            list: Passthrough to parse_cron_jobs().
        """
        server = GameServer.query.filter_by(id=self.server_id).first()

        cmd_id = 'list_jobs'
        cmd = ['crontab', '-l']

        if should_use_ssh(server):
            pass

        run_cmd_popen(cmd, cmd_id)
        proc_info = get_process(cmd_id)

        return self.parse_cron_jobs("".join(proc_info.stdout), server.id)


    def parse_cron_jobs(self, cron_text, target_uuid):
        """
        Parses jobs and comments, checks validity with croniter.

        Returns:
            list: Returns list of dictionaries with info about jobs for
                  matching uuid. 
        """
        jobs = []
        current_server_id = None
        current_job_id = None
        current_comment = None

        for line in cron_text.split('\n'):
            line = line.strip()

            # Track Ansible comments.
            if line.startswith('#Ansible:'):
                current_server_id = line.split(':')[1].strip()
                current_server_id = current_server_id.split(',')[0].strip()
                current_job_id = line.split(',')[1].strip()
                current_comment = line.split(',')[2].strip()
                continue

            # Skip other comments and empty lines.
            if not line or line.startswith('#'):
                current_server_id = None
                current_job_id = None
                current_comment = None
                continue

            # Split into schedule (first 5 fields) and command.
            parts = re.split(r'\s+', line, maxsplit=5)
            if len(parts) < 6:
                continue

            schedule = ' '.join(parts[:5])
            command = parts[5]

            # Validate with cron-converter.
            try:
                Cron(schedule)  # This should raise a ValueError if invalid.
                job = {
                    'schedule': schedule,
                    'command': command,
                    'server_id': current_server_id,
                    'job_id': current_job_id,
                    'comment': current_comment,
                }

                if current_server_id == target_uuid:
                    jobs.append(job)

            except ValueError:
                continue

            current_server_id = None
            current_job_id = None
            current_comment = None

        return jobs



