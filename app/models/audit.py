import shortuuid

from app import db
from sqlalchemy.sql import func
from sqlalchemy import event
from sqlalchemy.orm import Session

class Audit(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(shortuuid.uuid()),
        unique=True,  # Ensure uniqueness
        nullable=False,  # Ensure not null
    )
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True)
    message = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

    # Relationship to access the User directly
    user = db.relationship('User', backref='audit')

    def __repr__(self):
        return f"<Audit(id={self.id}, user_id='{self.user_id}', message='{self.message}', date_created='{self.date_created}')>"

    def __str__(self):
        return f"Audit (ID: {self.id},  Message: {self.message}, Created: {self.date_created})"


# Event listener for limiting audit records in DB to 1000 entries.
@event.listens_for(Audit, 'after_insert')
def after_audit_insert(mapper, connection, target):
    session = Session.object_session(target)
    if session is None:
        return

    # Count num audit records.
    count = session.query(Audit).count()

    # If we're over the limit, delete the oldest records.
    if count > 1000:
        # Calculate how many to delete.
        to_delete = count - 1000

        # Find the oldest records (order by date_created ascending).
        oldest_records = session.query(Audit).order_by(Audit.date_created.asc()).limit(to_delete).all()

        # Delete them.
        for record in oldest_records:
            session.delete(record)

        session.commit()


