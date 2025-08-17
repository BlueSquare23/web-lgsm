import uuid
import shortuuid

from app import db
from flask_login import UserMixin
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
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
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


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    role = db.Column(db.String(150))
    permissions = db.Column(db.String(600))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}', date_created='{self.date_created}')>"

    def __str__(self):
        return f"User {self.username} (ID: {self.id}, Role: {self.role}, Created: {self.date_created})"


class GameServer(db.Model):
    # Use UUIDs for game server IDs.
    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,  # Ensure uniqueness
        nullable=False,  # Ensure not null
    )
    # Unique name.
    install_name = db.Column(db.String(150))
    # Install path.
    install_path = db.Column(db.String(150))
    # The name of the lgsm game server script. For example, 'gmodserver'.
    script_name = db.Column(db.String(150))
    # Username of game server user.
    username = db.Column(db.String(150))
    # Is game server in a docker container or not.
    is_container = db.Column(db.Boolean())
    # Can be either local, remote, or docker.
    install_type = db.Column(db.String(150))
    # Hostname of remote installs.
    install_host = db.Column(db.String(150))
    # Has the game server installation finished.
    install_finished = db.Column(db.Boolean())
    # Private ssh keyfile path.
    keyfile_path = db.Column(db.String(150))

    def __repr__(self):
        return (
            f"<GameServer(id={self.id}, install_name='{self.install_name}', script_name='{self.script_name}', "
            + f"install_type='{self.install_type}', install_finished={self.install_finished} keyfile_path={self.keyfile_path})>"
        )

    def __str__(self):
        return (
            f"GameServer '{self.install_name}' (ID: {self.id}, Script: {self.script_name}, "
            + f"Type: {self.install_type}, Finished: {self.install_finished}, Keyfile Path: {self.keyfile_path})"
        )

    def delete(self):
        """Removes the GameServer entry from the database."""
        db.session.delete(self)
        db.session.commit()

