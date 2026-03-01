import re
import shortuuid

from cron_converter import Cron

from app.utils.paths import PATHS
from app import db

# TODO: All the below systems need clean arch refactored. For right now, cron
# is an early service that's getting the clean arch treatment, so leaving be.
# But will need cleaned up moving forward!
from app.config.config_manager import ConfigManager
#from app.models import GameServer
from app.infrastructure.persistence.repositories.game_server_repo import SqlAlchemyGameServerRepository

from app.domain.entities.job import Job
from app.services.proc_info.proc_info_registry import ProcInfoRegistry
from app.services.command_exec.command_executor import CommandExecutor

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

    config = ConfigManager()
    command_service = CommandExecutor(config)

    def update(self, job):
        """
        Updates / Create job in system crontab.
        """
        # Then, add job to system crontab for user via connector.
        cmd = CronScheduler.CONNECTOR_CMD + ["--cron", job.job_id]

        cmd_id = f'add_job_{job.job_id}'
        self.command_service.run_command(cmd, None, cmd_id)

        proc_info = ProcInfoRegistry().get_process(cmd_id)
        print(proc_info.stderr)

        if proc_info == None:
            return False

        if proc_info.exit_status > 0:
            return False

        return True


    def delete(self, job):
        """
        Delete cronjob entries from the system crontab.

        Returns:
            Bool: True if could delete, False otherwise.
        """
        # Remove job from system crontab.
        cmd = CronScheduler.CONNECTOR_CMD + ["--cron", job.job_id, "--delete", job.server_id]

        cmd_id = f'delete_job_{job.job_id}'
        self.command_service.run_command(cmd, None, cmd_id)
        proc_info = ProcInfoRegistry().get_process(cmd_id)

        if proc_info == None:
            return False

        if proc_info.exit_status > 0:
            return False

        return True


    def list(self, server_id):
        """
        Used for getting list of jobs for associated game server.

        Returns:
            list: Passthrough to parse_cron_jobs().
        """
        # TODO: UGH... I forgot I made this whole thing per game server. So for now
        # keeping this as is. I don't think its terrible because it is going from
        # infra -> infra layer. But ideally no db stuff should be happening in
        # this class! Will get there as I refactor more.
#        server = GameServer.query.filter_by(id=server_id).first()
        repo = SqlAlchemyGameServerRepository()
        server = repo.get(server_id)

        cmd_id = 'list_jobs'
        cmd = [PATHS['crontab'], '-l']

        self.command_service.run_command(cmd, server, cmd_id)

        proc_info = ProcInfoRegistry().get_process(cmd_id)

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
                kwargs = {
                    'schedule': schedule,
                    'command': command,
                    'server_id': current_server_id,
                    'job_id': current_job_id,
                    'comment': current_comment,
                }
                job = Job(**kwargs)

                if current_server_id == target_uuid:
                    jobs.append(job)

            except ValueError:
                continue

            current_server_id = None
            current_job_id = None
            current_comment = None

        return jobs


