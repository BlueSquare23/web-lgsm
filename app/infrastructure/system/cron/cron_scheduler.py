import re
import shortuuid
import copy

from cron_converter import Cron

from app.utils.paths import PATHS
from app import db

from app.infrastructure.persistence.repositories.game_server_repo import SqlAlchemyGameServerRepository
from app.infrastructure.persistence.repositories.cron_repo import SqlAlchemyCronRepository
from app.infrastructure.system.repositories.proc_info_repo import InMemProcInfoRepository

from app.domain.entities.job import Job
from app.infrastructure.system.command_executor.command_executor import CommandExecutor
from app.infrastructure.system.user.user_module_service import UserModuleService

class CronScheduler:
    """
    Infrastructure layer class for interacting with the systems crontab via the
    ansible connector.
    """
    CONNECTOR_CMD = [
        PATHS["sudo"],
        "-n",
        "/opt/web-lgsm/bin/python",
        PATHS["ansible_connector"],
    ]

    # Dep invert these to make testing easier
    def __init__(self, command_service=CommandExecutor(), module_service=UserModuleService(), game_server_repo=SqlAlchemyGameServerRepository(), cron_repo=SqlAlchemyCronRepository()):
        self.command_service = command_service
        self.module_service = module_service
        self.game_server_repo = game_server_repo
        self.cron_repo = cron_repo
    

    def update(self, job, state=True):
        """
        Updates / Create job in system crontab.
        """
        server = self.game_server_repo.get(job.server_id)

        args = [ state ]

        kwargs = job.__dict__
        kwargs['install_path'] = server.install_path
        kwargs['script_name'] = server.script_name
        kwargs['as_user'] = server.username

        return self.module_service.call('edit_cron', *args, **kwargs)


    def delete(self, job_id):
        """
        Delete cronjob entries from the system crontab. 
        Wraps update with delete=True

        Returns:
            Bool: True if could delete, False otherwise.
        """
        job = self.cron_repo.get(job_id)
        if not job:
            return False

        return self.update(job, state=False)


    def list(self, server_id):
        """
        Used for getting list of jobs for associated game server.

        Returns:
            list: Passthrough to parse_cron_jobs().
        """
        server = self.game_server_repo.get(server_id)

        cmd_id = 'list_jobs'
        InMemProcInfoRepository().remove(cmd_id)  # Clear any old proc_info objects

        cmd = [PATHS['crontab'], '-l']

        self.command_service.run(cmd, server, cmd_id)

        proc_info = InMemProcInfoRepository().get(cmd_id)

        return self.parse_cron_jobs("".join(proc_info.stdout), server.id)


    def parse_cron_jobs(self, cron_text, target_uuid):
        jobs = []
        current_server_id = None
        current_job_id = None
        current_comment = None

        for line in cron_text.split('\n'):
            line = line.strip()

            # Handle Ansible-style header (For backward compat)
            if line.startswith('#Ansible:'):
                try:
                    meta = line.replace('#Ansible:', '').strip()
                    parts = [p.strip() for p in meta.split(',', 2)]
    
                    current_server_id = parts[0]
                    current_job_id = parts[1] if len(parts) > 1 else None
                    current_comment = parts[2] if len(parts) > 2 else None
                except Exception:
                    current_server_id = None
                    current_job_id = None
                    current_comment = None
                continue

            # Skip empty lines
            if not line:
                continue

            # Extract inline comment (CronTab style)
            inline_server_id = None
            inline_job_id = None
            inline_comment = None

            if '#' in line:
                line, inline_meta = line.split('#', 1)
                inline_meta = inline_meta.strip()

                try:
                    parts = [p.strip() for p in inline_meta.split(',', 2)]
                    inline_server_id = parts[0]
                    inline_job_id = parts[1] if len(parts) > 1 else None
                    inline_comment = parts[2] if len(parts) > 2 else None
                except Exception:
                    pass

            # Parse cron fields
            parts = re.split(r'\s+', line.strip(), maxsplit=5)
            if len(parts) < 6:
                # reset ansible metadata if line invalid
                current_server_id = None
                current_job_id = None
                current_comment = None
                continue

            # NOTE: We kinda fudge command here. Normally command is just
            # one word arg (start, stop, details, etc.) whereas here we make it
            # the full cronjob cmd string for better display on frontend.
            schedule = ' '.join(parts[:5])
            command = parts[5]

            # Choose metadata source
            server_id = inline_server_id or current_server_id
            job_id = inline_job_id if inline_job_id else current_job_id
            comment = inline_comment if inline_comment else current_comment

            # Validate cron
            try:
                Cron(schedule)

                kwargs = {
                    'schedule': schedule,
                    'command': command,
                    'server_id': server_id,
                    'job_id': job_id,
                    'comment': comment,
                }
                job = Job(**kwargs)

                if server_id == target_uuid:
                    jobs.append(job)

                # Strip path from command for DB entry.
                job_copy = copy.copy(job)
                command_parts = command.split(' ')
                job_copy.command = command_parts[-1]

                # Ensure DB entry for job matches file system
                self.cron_repo.update(job_copy)

            except ValueError:
                pass

            # Reset Ansible-style metadata
            current_server_id = None
            current_job_id = None
            current_comment = None

        return jobs

