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
        lines = [l.strip() for l in cron_text.split('\n')]

        def parse_meta(meta_str):
            try:
                parts = [p.strip() for p in meta_str.split(',', 2)]
                server_id = parts[0] if len(parts) > 0 else None
                job_id = parts[1] if len(parts) > 1 else None
                comment = parts[2] if len(parts) > 2 else None
                return server_id, job_id, comment
            except Exception:
                return None, None, None

        def is_valid_uuid_like(val):
            return bool(val and re.match(r'^[a-f0-9\-]{36}$', val))
    
        for i, raw_line in enumerate(lines):
            if not raw_line or raw_line.startswith('#'):
                continue
    
            line = raw_line
    
            # 1. Extract inline metadata
            inline_server_id = None
            inline_job_id = None
            inline_comment = None
    
            if ' #' in line:  # safer than just '#'
                line, inline_meta = line.split(' #', 1)
                inline_meta = inline_meta.strip()
                inline_server_id, inline_job_id, inline_comment = parse_meta(inline_meta)
    
            # 2. Parse cron fields
            parts = re.split(r'\s+', line.strip(), maxsplit=5)
            if len(parts) < 6:
                continue
    
            schedule = ' '.join(parts[:5])
            command = parts[5]
    
            # 3. Validate cron
            try:
                Cron(schedule)
            except ValueError:
                continue
    
            # 4. Fallback to previous line (Ansible-style, for backward compat)
            server_id = inline_server_id
            job_id = inline_job_id
            comment = inline_comment
    
            if not (server_id and job_id) and i > 0:
                prev_line = lines[i - 1]
                if prev_line.startswith('#Ansible:'):
                    meta = prev_line.replace('#Ansible:', '').strip()
                    s_id, j_id, cmt = parse_meta(meta)
    
                    server_id = server_id or s_id
                    job_id = job_id or j_id
                    comment = comment or cmt
    
            # 5. Build job object
            job = Job(
                schedule=schedule,
                command=command,
                server_id=server_id,
                job_id=job_id,
                comment=comment,
            )
    
            # 6. Classify job
            is_managed = (
                is_valid_uuid_like(server_id) and
                bool(job_id)
            )
    
            job.is_managed = is_managed
    
            # 7. Unmanaged jobs (greyed out)
            if not is_managed:
                jobs.append(job)
                continue
    
            # 8. Managed jobs (normal flow)
            if server_id == target_uuid:
                jobs.append(job)
    
                # Sync DB
                job_copy = copy.copy(job)
                command_parts = command.split(' ')
                job_copy.command = command_parts[-1]
    
                self.cron_repo.update(job_copy)
    
        return jobs

