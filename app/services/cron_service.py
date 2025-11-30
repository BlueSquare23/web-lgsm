import re
import shortuuid

from cron_converter import Cron

from app.models import GameServer, Job
from app.utils import should_use_ssh, run_cmd_ssh, run_cmd_popen
from app.utils.paths import PATHS
from app import db

# Has to be local import to avoid circular import
from .proc_info_service import ProcInfoService

"""
Service class interface for interacting with system cron from API and jobs
route.
"""

class CronService:
    CONNECTOR_CMD = [
        PATHS["sudo"],
        "-n",
        "/opt/web-lgsm/bin/python",
        PATHS["ansible_connector"],
    ]

    def __init__(self, server_id):
        self.server_id = server_id 


    def edit_job(self, job):
        """
        Updates / Create job in database and wraps invocation of ansible
        connector for cron job edits.

        Args:
            job (dict): Job to create.

        Returns:
            bool: True if job created successfully, False otherwise.
        """
        cronjob = Job.query.filter_by(id=job["job_id"]).first()
        newjob = False

        # First, add/update job in database.
        if cronjob == None:
            newjob = True
            cronjob = Job()
        else:
            # If existing job, del old job first. Inefficient, but keeps state
            # clean. 
            self.delete_job(cronjob.id, del_db_entry=False)

        cronjob.server_id = job["server_id"]
        cronjob.command = job["command"]
        cronjob.comment = job["comment"]
        cronjob.expression = job["expression"]

        if newjob:
            db.session.add(cronjob)
        db.session.commit()

        # Then, add job to system crontab for user via connector.
        cmd = CronService.CONNECTOR_CMD + ["--cron", cronjob.id]

        cmd_id = f'add_job_{cronjob.id}'
        run_cmd_popen(cmd, cmd_id)
        proc_info = ProcInfoService().get_process(cmd_id)

        if proc_info == None:
            return False

        if proc_info.exit_status > 0:
            return False

        return True


    def delete_job(self, job_id, del_db_entry=True):
        """
        Delete cronjob entries from DB & system crontab.

        Args:
            job_id (str(shortuuid)): Id of job to delete.
            del_db_entry (bool): Should delete or keep database entry for job.
                                 Used for edit_job to purge old job from crontab first. 
        Returns:
            bool: True if job removed successfully, False otherwise.
        """
        cronjob = Job.query.filter_by(id=job_id).first()
        if cronjob == None:
            return False

        # Remove job from system crontab.
        cmd = CronService.CONNECTOR_CMD + ["--cron", cronjob.id, "--delete", self.server_id]

        cmd_id = f'delete_job_{cronjob.id}'
        run_cmd_popen(cmd, cmd_id)
        proc_info = ProcInfoService().get_process(cmd_id)

        if proc_info == None:
            return False

        if proc_info.exit_status > 0:
            return False

        if not del_db_entry:
            return True

        # Remove job from DB.
        db.session.delete(cronjob)
        db.session.commit()
        return True


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
            run_cmd_ssh(cmd, server, False, 5.0, cmd_id) 
        else:
            run_cmd_popen(cmd, cmd_id)

        proc_info = ProcInfoService().get_process(cmd_id)

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



