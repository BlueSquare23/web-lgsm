import shortuuid

from app.domain.repositories.cron_repo import CronRepository
from app.domain.entities.job import Job 
from app.infrastructure.persistence.models.cron_model import CronModel
from app import db

class SqlAlchemyCronRepository(CronRepository):

    def add(self, job):
        model = CronModel(
            id=str(shortuuid.uuid()),  # Always set new shortuuid
            server_id=job.server_id,
            schedule=job.schedule,
            command=job.command,
            comment=job.comment,
        )
        db.session.add(model)
        db.session.commit()
        return model.id

    def update(self, job):
        model = CronModel.query.filter_by(id=job.job_id).first()

        # If job doesn't exist, add it.
        if model == None:
            return self.add(job)

        for key, value in job.__dict__.items():
            if key == 'job_id':
                continue
            setattr(model, key, value)

        db.session.commit()
        return True

    def get(self, job_id):
        """Convert job_id into Job entity"""
        model = CronModel.query.filter_by(id=job_id).first()

        # If job doesn't exist, add it.
        if model == None:
            return None

        # Convert model object to Job entity.
        data = {
            'job_id': model.id,
            'server_id': model.server_id,
            'schedule': model.schedule,
            'command': model.command,
            'comment': model.comment,
        }
        job = Job(**data)

        return job

    def delete(self, job_id):
        cronjob = CronModel.query.filter_by(id=job_id).first()

        if not cronjob:
            return False

        db.session.delete(cronjob)
        db.session.commit()
        return True

    def list(self):
        raise NotImplementedError
        # TODO: Eventually, we'll want to use the DB to fetch known added jobs,
        # and only depend on system cron for unknown (aka not added aka greyed
        # out jobs). But we're not there yet. Right now all list comes from
        # system.

