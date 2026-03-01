import uuid

from app import db

class GameServerModel(db.Model):
    # Use UUIDs for game server IDs.
    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,  # Ensure uniqueness
        nullable=False,  # Ensure not null
    )
    # Name.
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
    # Did something go wrong and the install was aborted.
    install_failed = db.Column(db.Boolean())
    # Private ssh keyfile path.
    keyfile_path = db.Column(db.String(150))

    def __repr__(self):
        return (
            f"<GameServer(id={self.id}, install_name='{self.install_name}', script_name='{self.script_name}', "
            + f"install_type='{self.install_type}', install_finished={self.install_finished} keyfile_path={self.keyfile_path})>"
        )

    def __str__(self):
        return (
            f"GameServer '{self.install_name}' (ID: {self.id}, Script: {self.script_name}, Username: {self.username}, "
            + f"Type: {self.install_type}, Host: {self.install_host}, Finished: {self.install_finished}, Keyfile Path: {self.keyfile_path})"
        )

