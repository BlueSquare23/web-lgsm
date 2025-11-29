import shortuuid

from app import db
from sqlalchemy.sql import func

class Job(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(shortuuid.uuid()),
        unique=True,  # Ensure uniqueness
        nullable=False,  # Ensure not null
    )
    server_id = db.Column(db.String(36), db.ForeignKey('game_server.id'), nullable=False)
    command = db.Column(db.String(150))
    comment = db.Column(db.String(150))
    expression = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

    # Relationship to access the GameServer directly
    game_server = db.relationship('GameServer', backref='jobs')

    def __repr__(self):
        return f"<Job(id={self.id}, server_id='{self.server_id}', command='{self.command}', comment='{self.comment}', expression='{self.expression}', date_created='{self.date_created}')>"

    def __str__(self):
        return f"Job (ID: {self.id}, Command: {self.command}, Comment: {self.comment}, Expression: {self.expression}, Created: {self.date_created})"


