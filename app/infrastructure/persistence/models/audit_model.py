import shortuuid

from app import db
from sqlalchemy.sql import func
from sqlalchemy import event
from sqlalchemy.orm import Session

class AuditModel(db.Model):
    """
    Audit sqlalchemy model.
    """
    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(shortuuid.uuid()),
        unique=True,  # Ensure uniqueness
        nullable=False,  # Ensure not null
    )
    user_id = db.Column(db.String(36), db.ForeignKey('user_model.id'), nullable=True)
    message = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

    # Relationship to access the User directly
    user = db.relationship('UserModel', backref='audit_model')


    def __repr__(self):
        return f"<Audit(id={self.id}, user_id='{self.user_id}', message='{self.message}', date_created='{self.date_created}')>"

    def __str__(self):
        return f"Audit (ID: {self.id},  Message: {self.message}, Created: {self.date_created})"

